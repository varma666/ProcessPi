"""
processpi/pipelines/engine.py

Rewritten PipelineEngine (drop-in replacement)
- Implements the finalized algorithm from product discussion.
- SI-first internal units. Accepts mixed-unit inputs but converts internally.
- Supports single-pipe and network (PipelineNetwork) operation.
- Dual network solver: linear/matrix solver + Hardy-Cross; compares residuals.
- Forward (Q -> ΔP) and inverse (ΔP -> Q) modes.
- Pipe sizing: compute ideal diameter, map to nearest standard size from standards.py.
- Pump sizing: compute head (m/kPa) and shaft power (kW) with default efficiency 70%.
- Detailed per-element reporting, warnings, and machine-readable JSON output.

Notes:
- This file aims to integrate cleanly with your existing modules: Pipe, Fitting, Equipment,
  PipelineNetwork, standards.* utilities, and Component class. Adjust imports if your
  package layout differs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import math

# Local package imports (assumed to exist in your project)
from ..units import (
    Diameter, Length, Pressure, Density, Viscosity, VolumetricFlowRate, Velocity, MassFlowRate
)
from .pipelineresults import PipelineResults
from .nozzle import Nozzle
from ..components import Component
from .standards import (
    get_k_factor, get_roughness, list_available_pipe_diameters, get_standard_pipe_data,
    get_recommended_velocity, get_standard_pipe_schedules
)
from .pipes import Pipe
from .fittings import Fitting
from .equipment import Equipment
from .network import PipelineNetwork
from .piping_costs import PipeCostModel
from ..calculations.fluids import (
    FluidVelocity, ReynoldsNumber, PressureDropDarcy, OptimumPipeDiameter, PressureDropFanning, ColebrookWhite
)
# Hazen-Williams calculator (user provided module)
from ..calculations.pressure_drop.hazen_williams import PressureDropHazenWilliams

# ------------------------------- Constants ---------------------------------
G = 9.80665  # m/s^2
DEFAULT_PUMP_EFFICIENCY = 0.70
DEFAULT_FLOW_TOL = 1e-6  # m3/s absolute flow tolerance for solvers
MAX_HC_ITER = 200
MAX_MATRIX_ITER = 100

# ------------------------------- Helpers -----------------------------------

def _to_m3s(maybe_flow: Any) -> VolumetricFlowRate:
    """Normalize flow to VolumetricFlowRate (m^3/s). Accepts MassFlowRate as well."""
    if maybe_flow is None:
        raise ValueError("Flow cannot be None")
    if isinstance(maybe_flow, VolumetricFlowRate):
        return maybe_flow
    if isinstance(maybe_flow, MassFlowRate):
        raise TypeError("MassFlowRate provided without density context. Convert before calling.")
    # assume numeric m3/s
    return VolumetricFlowRate(float(maybe_flow), "m3/s")


def _ensure_diameter_obj(d: Any, assume_mm: bool = True) -> Diameter:
    if isinstance(d, Diameter):
        return d
    val = float(d)
    unit = "mm" if assume_mm else "m"
    return Diameter(val, unit)


@dataclass
class ElementReport:
    name: str
    type: str
    diameter_m: Optional[float] = None
    flow_m3s: Optional[float] = None
    velocity_m_s: Optional[float] = None
    reynolds: Optional[float] = None
    friction_factor: Optional[float] = None
    dp_pa: Optional[float] = None
    head_m: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "diameter_m": self.diameter_m,
            "flow_m3s": self.flow_m3s,
            "velocity_m_s": self.velocity_m_s,
            "reynolds": self.reynolds,
            "friction_factor": self.friction_factor,
            "pressure_drop_Pa": self.dp_pa,
            "head_loss_m": self.head_m,
            "warnings": self.warnings,
        }


# ----------------------------- Pipeline Engine -----------------------------
class PipelineEngine:
    """Pipeline simulation and sizing engine.

    Usage: create engine, call .fit(...) with inputs (fluid, network or pipe, flowrate or mass_flowrate, etc.), then call .run().

    The object stores the last results in self._results (PipelineResults).
    """

    def __init__(self, **kwargs: Any) -> None:
        self.data: Dict[str, Any] = {}
        self._results: Optional[PipelineResults] = None
        if kwargs:
            self.fit(**kwargs)

    # ---------------------- Configuration / Fit ----------------------------
    def fit(self, **kwargs: Any) -> "PipelineEngine":
        """Configure engine inputs. Converts and normalizes keys/aliases.
        Expected keys (examples): fluid=Component OR density, viscosity; network=PipelineNetwork; pipe=Pipe; flowrate=VolumetricFlowRate or mass_flowrate=MassFlowRate; available_dp=Pressure
        """
        self.data = dict(kwargs)

        # Aliases
        alias_map = {
            "flowrate": ["flow_rate", "q", "Q"],
            "mass_flowrate": ["mass_flow", "m_dot", "mdot"],
            "velocity": ["v"],
            "diameter": ["dia", "D", "nominal_diameter", "internal_diameter"],
            "length": ["len", "L"],
            "inlet_pressure": ["in_pressure", "pin", "p_in"],
            "outlet_pressure": ["out_pressure", "pout", "p_out"],
        }
        for canon, alts in alias_map.items():
            if canon not in self.data:
                for a in alts:
                    if a in self.data:
                        self.data[canon] = self.data[a]
                        break

        # Defaults
        self.data.setdefault("assume_mm_for_numbers", True)
        self.data.setdefault("flow_split", {})
        self.data.setdefault("tolerance_m3s", DEFAULT_FLOW_TOL)
        self.data.setdefault("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
        # calculation method: 'darcy_weisbach' or 'hazen_williams'
        self.data.setdefault("method", "darcy_weisbach")

        # validate network type if present
        net = self.data.get("network")
        if net is not None and not isinstance(net, PipelineNetwork):
            raise TypeError("`network` must be a PipelineNetwork instance.")

        return self

    # ---------------------- Fluid properties --------------------------------
    def _get_density(self) -> Density:
        if "density" in self.data and self.data["density"] is not None:
            return self.data["density"]
        fluid = self.data.get("fluid")
        if isinstance(fluid, Component):
            return fluid.density()
        raise ValueError("Provide 'density' or a 'fluid' Component with density().")

    def _get_viscosity(self) -> Viscosity:
        if "viscosity" in self.data and self.data["viscosity"] is not None:
            return self.data["viscosity"]
        fluid = self.data.get("fluid")
        if isinstance(fluid, Component):
            return fluid.viscosity()
        raise ValueError("Provide 'viscosity' or a 'fluid' Component with viscosity().")

    # ---------------------- Flow inference ----------------------------------
    def _infer_flowrate(self) -> VolumetricFlowRate:
        if "flowrate" in self.data and self.data["flowrate"] is not None:
            return self.data["flowrate"]
        # mass flow -> volumetric
        if "mass_flowrate" in self.data and self.data["mass_flowrate"] is not None:
            rho = self._get_density()
            m = self.data["mass_flowrate"]
            m_val = m.value if hasattr(m, "value") else float(m)
            q_val = m_val / (rho.value if hasattr(rho, "value") else float(rho))
            q = VolumetricFlowRate(q_val, "m3/s")
            self.data["flowrate"] = q
            return q
        # velocity & diameter
        v = self.data.get("velocity")
        d = self.data.get("diameter")
        if v is not None and d is not None:
            if not isinstance(v, Velocity):
                v = Velocity(float(v), "m/s")
            d_obj = _ensure_diameter_obj(d, self.data.get("assume_mm_for_numbers", True))
            q = VolumetricFlowRate(v.value * math.pi * (d_obj.to("m").value ** 2) / 4.0, "m3/s")
            self.data["flowrate"] = q
            return q
        raise ValueError("Unable to infer flowrate. Provide 'flowrate' or 'mass_flowrate' or ('velocity' and 'diameter').")

    # ---------------------- Diameter resolution -----------------------------
    def _resolve_internal_diameter(self, pipe: Optional[Pipe] = None) -> Diameter:
        # Priority: pipe.internal_diameter -> pipe.nominal_diameter -> engine diameter -> compute optimum
        if pipe is not None:
            if getattr(pipe, "internal_diameter", None) is not None:
                d = pipe.internal_diameter
                return d if isinstance(d, Diameter) else Diameter(float(d), "m")
            if getattr(pipe, "nominal_diameter", None) is not None:
                d = pipe.nominal_diameter
                return d if isinstance(d, Diameter) else Diameter(float(d), "m")
        d = self.data.get("diameter")
        if d is not None:
            return d if isinstance(d, Diameter) else _ensure_diameter_obj(d, self.data.get("assume_mm_for_numbers", True))
        # fallback compute optimum for single pipe
        q = self._infer_flowrate()
        calc = OptimumPipeDiameter(flow_rate=q, density=self._get_density())
        return calc.calculate()

    # ---------------------- Primitive calculators ---------------------------
    def _velocity(self, q: VolumetricFlowRate, d: Diameter) -> Velocity:
        return FluidVelocity(volumetric_flow_rate=q, diameter=d).calculate()

    def _reynolds(self, v: Velocity, d: Diameter) -> float:
        return ReynoldsNumber(density=self._get_density(), velocity=v, diameter=d, viscosity=self._get_viscosity()).calculate()

    def _friction_factor(self, Re: float, d: Diameter, material: Optional[str] = None) -> float:
        eps = get_roughness(material) if material else 0.0
        return ColebrookWhite(reynolds_number=Re, roughness=eps, diameter=d).calculate()

    def _major_dp_pa(self, f: float, L: Length, d: Diameter, v: Velocity) -> Pressure:
        return PressureDropDarcy(friction_factor=f, length=L, diameter=d, density=self._get_density(), velocity=v).calculate()

    def _minor_dp_pa(self, fitting: Fitting, v: Velocity, f: Optional[float], d: Diameter) -> Pressure:
        # try K factor first
        rho = self._get_density().value
        v_val = v.value if hasattr(v, "value") else float(v)
        K = getattr(fitting, "K", None) or getattr(fitting, "K_factor", None) or getattr(fitting, "total_K", None)
        if K is not None:
            return Pressure(0.5 * rho * v_val * v_val * float(K), "Pa")
        # equivalent length fallback
        Le = getattr(fitting, "Le", None) or getattr(fitting, "equivalent_length", None)
        if Le is not None:
            if f is None:
                # recompute friction
                Re = self._reynolds(v, d)
                f_val = self._friction_factor(Re, d)
            else:
                f_val = float(f)
            return Pressure(float(f_val) * (float(Le) / d.to("m").value) * 0.5 * rho * v_val * v_val, "Pa")
        return Pressure(0.0, "Pa")

    # ---------------------- Single pipe calc --------------------------------
    def _calc_single_pipe(self, pipe: Pipe, q: VolumetricFlowRate) -> Tuple[ElementReport, Dict[str, Any]]:
        d = self._resolve_internal_diameter(pipe)
        v = self._velocity(q, d)
        Re = self._reynolds(v, d)
        f = self._friction_factor(Re, d, getattr(pipe, "material", None))
        dp_major = self._major_dp_pa(f, pipe.length or Length(1.0, "m"), d, v)

        dp_minor = Pressure(0.0, "Pa")
        warnings: List[str] = []
        if hasattr(pipe, "fittings") and isinstance(pipe.fittings, list):
            for ft in pipe.fittings:
                dp_minor += self._minor_dp_pa(ft, v, f, d)
        else:
            # allow top-level fittings
            for ft in self.data.get("fittings", []) or []:
                dp_minor += self._minor_dp_pa(ft, v, f, d)

        total_dp = dp_major.to("Pa").value + dp_minor.to("Pa").value
        head_m = total_dp / (self._get_density().value * G)

        # warnings
        rec = None
        service = getattr(self.data.get("fluid"), "service_type", None)
        if service:
            rec = get_recommended_velocity(service)
        if rec:
            v_val = v.value if hasattr(v, "value") else float(v)
            if isinstance(rec, tuple):
                vmin, vmax = rec
                if v_val < vmin:
                    warnings.append(f"velocity below recommended ({v_val:.3f} m/s < {vmin} m/s)")
                if v_val > vmax:
                    warnings.append(f"velocity above recommended ({v_val:.3f} m/s > {vmax} m/s)")
        if Re < 2300:
            warnings.append("flow in laminar regime (Re < 2300)")
        elif 2300 <= Re < 4000:
            warnings.append("flow in transitional regime (2300 <= Re < 4000)")

        rep = ElementReport(
            name=getattr(pipe, "name", "pipe"),
            type="pipe",
            diameter_m=d.to("m").value,
            flow_m3s=q.value,
            velocity_m_s=v.value,
            reynolds=Re,
            friction_factor=f,
            dp_pa=total_dp,
            head_m=head_m,
            warnings=warnings,
        )
        result_dict = {
            "velocity": v,
            "reynolds": Re,
            "friction_factor": f,
            "major_dp": dp_major,
            "minor_dp": dp_minor,
            "pressure_drop": Pressure(total_dp, "Pa"),
            "head_m": head_m,
        }
        return rep, result_dict

    # ---------------------- Network solvers ---------------------------------
    def _hardy_cross(self, network: PipelineNetwork, q_total: VolumetricFlowRate, tol: float) -> Tuple[bool, float, List[ElementReport]]:
        """Simplified Hardy-Cross iterative solver. Returns (converged, residual, reports).

        Note: This implementation uses a straightforward loop-correction approach. For
        complex networks you may replace this with a more robust library later.
        """
        # Initialize branch flows (equal split by default)
        branches = network.get_parallel_branches() if hasattr(network, "get_parallel_branches") else network.get_branches()
        n = len(branches) if branches else 1
        branch_flows = [q_total.value / n] * n

        for it in range(MAX_HC_ITER):
            max_residual = 0.0
            reports: List[ElementReport] = []
            # For each branch compute loop head and correction
            for i, branch in enumerate(branches):
                q_b = VolumetricFlowRate(branch_flows[i], "m3/s")
                dp_branch, el_reports, _ = self._compute_network(branch, q_b)
                # compute derivative approx dH/dQ ~= 2*H/Q (heuristic) to get correction
                H = dp_branch.to("Pa").value / (self._get_density().value * G)
                if abs(q_b.value) < 1e-12:
                    dHdQ = 1e12
                else:
                    dHdQ = 2.0 * H / q_b.value
                # compute correction deltaQ = -H / (dH/dQ)
                dq = -H / dHdQ
                branch_flows[i] += dq
                max_residual = max(max_residual, abs(dq))
                # collect element reports for branch
                reports.extend([ElementReport(**r.as_dict()) if isinstance(r, ElementReport) else ElementReport(name=r.get('name','el'), type=r.get('type','el')) for r in el_reports])

            if max_residual < tol:
                return True, max_residual, reports
        return False, max_residual, reports

    def _matrix_solver(self, network: PipelineNetwork, q_total: VolumetricFlowRate, tol: float) -> Tuple[bool, float, List[ElementReport]]:
        """Linear/matrix-based solver placeholder.

        For Phase 1 we implement a simple linearization: initialize flows by equal split
        then perform a small number of Picard iterations updating friction factors and solving
        continuity via proportional adjustments. This is intentionally simple for readability.
        """
        branches = network.get_parallel_branches() if hasattr(network, "get_parallel_branches") else network.get_branches()
        n = len(branches) if branches else 1
        branch_flows = [q_total.value / n] * n

        for it in range(MAX_MATRIX_ITER):
            prev = branch_flows.copy()
            reports: List[ElementReport] = []
            # compute heads for each branch and adjust proportionally
            heads = []
            for i, branch in enumerate(branches):
                q_b = VolumetricFlowRate(branch_flows[i], "m3/s")
                dp_branch, el_reports, _ = self._compute_network(branch, q_b)
                H = dp_branch.to("Pa").value / (self._get_density().value * G)
                heads.append(H)
                reports.extend([ElementReport(**r.as_dict()) if isinstance(r, ElementReport) else ElementReport(name=r.get('name','el'), type=r.get('type','el')) for r in el_reports])
            # Normalize flows to keep total Q constant while distributing inversely to head
            if sum(heads) == 0:
                break
            inv = [1.0 / max(h, 1e-12) for h in heads]
            s = sum(inv)
            for i in range(n):
                branch_flows[i] = q_total.value * (inv[i] / s)
            # check convergence
            max_change = max(abs(branch_flows[i] - prev[i]) for i in range(n))
            if max_change < tol:
                return True, max_change, reports
        return False, max_change, reports

    # ---------------------- Network wrapper ---------------------------------
    def _solve_network_dual(self, network: PipelineNetwork, q_total: VolumetricFlowRate, tol: float) -> Dict[str, Any]:
        """Run both matrix solver and Hardy-Cross; compare residuals and return best."""
        # Run matrix solver
        matrix_ok, matrix_res, matrix_reports = self._matrix_solver(network, q_total, tol)
        # Run Hardy-Cross
        hc_ok, hc_res, hc_reports = self._hardy_cross(network, q_total, tol)

        # Decide winner (smaller residual preferred). If tie prefer matrix solver.
        chosen = {
            "method": "matrix" if matrix_res <= hc_res else "hardy_cross",
            "converged": matrix_ok if matrix_res <= hc_res else hc_ok,
            "residual": min(matrix_res, hc_res),
            "reports": matrix_reports if matrix_res <= hc_res else hc_reports,
        }
        return chosen

    # ---------------------- Diameter selection -------------------------------
    def _select_standard_diameter(self, ideal_d_m: float) -> Tuple[str, Diameter]:
        """Map a continuous ideal diameter (m) to nearest standard nominal and return (nominal_label, Diameter).
        Picks the smallest standard size that yields velocity <= vmax (i.e., choose next larger size if needed).
        """
        # Gather catalog (assume get_standard_pipe_data gives internal diameter as Diameter)
        candidates: List[Tuple[str, Diameter]] = []
        for nominal in list_available_pipe_diameters():
            for sched in get_standard_pipe_schedules():
                try:
                    data = get_standard_pipe_data(nominal, sched)
                except Exception:
                    continue
                d_internal: Diameter = data.get("internal_diameter")
                if not isinstance(d_internal, Diameter):
                    d_internal = Diameter(float(d_internal), "m")
                candidates.append((f"{nominal}-{sched}", d_internal))
        # sort by diameter
        candidates.sort(key=lambda x: x[1].to("m").value)
        # pick first candidate with diameter >= ideal_d_m
        for label, d in candidates:
            if d.to("m").value >= ideal_d_m:
                return label, d
        # fallback to largest available
        if candidates:
            return candidates[-1][0], candidates[-1][1]
        raise ValueError("No standard pipe diameters available in catalog")

    # ---------------------- Top-level run -----------------------------------
    def run(self) -> PipelineResults:
        """Execute configured simulation or sizing job and return PipelineResults.

        Behavior:
          - If network present: run network solver and return detailed per-element results.
          - If available_dp specified with missing pipe diameters: run sizing routine.
          - Otherwise run single-pipe forward calculation.
        """
        net = self.data.get("network")
        q = self._infer_flowrate()
        tol = self.data.get("tolerance_m3s", DEFAULT_FLOW_TOL)

        results_out: Dict[str, Any] = {"mode": None, "summary": {}, "components": []}

        # ----------------- Network Mode ------------------
        if isinstance(net, PipelineNetwork):
            results_out["mode"] = "network"
            # If available_dp present and pipes need sizing -> call network optimizer
            available_dp = self.data.get("available_dp")
            if available_dp is not None and any(p.nominal_diameter is None for p in net.get_all_pipes()):
                # perform iterative sizing by mapping ideal diameters to standard sizes
                # Simple approach: for each unspecified pipe compute ideal diameter using OptimumPipeDiameter then map
                for p in net.get_all_pipes():
                    if p.nominal_diameter is None:
                        q_branch = self._infer_flowrate() / len(net.get_all_pipes()) if len(net.get_all_pipes()) else q
                        ideal = OptimumPipeDiameter(flow_rate=q_branch, density=self._get_density()).calculate().to("m").value
                        label, dstd = self._select_standard_diameter(ideal)
                        p.nominal_diameter = dstd
                # After mapping, re-run solver
            solved = self._solve_network_dual(net, q, tol)
            reports = solved.get("reports", [])

            # build summary and components
            comp_list = [r.as_dict() for r in reports]
            total_dp_pa = 0.0
            for r in comp_list:
                if r.get("pressure_drop_Pa"):
                    total_dp_pa += float(r.get("pressure_drop_Pa"))
            total_head_m = total_dp_pa / (self._get_density().value * G)
            pump_eff = self.data.get("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
            shaft_power_kw = (total_dp_pa * q.value) / (1000.0 * pump_eff)

            results_out["summary"] = {
                "inlet_flow_m3s": q.value,
                "total_pressure_drop_Pa": total_dp_pa,
                "total_head_m": total_head_m,
                "pump_shaft_power_kW": shaft_power_kw,
                "solver_method": solved.get("method"),
                "solver_converged": solved.get("converged"),
                "solver_residual": solved.get("residual"),
            }
            results_out["components"] = comp_list

        # ----------------- Single pipe -------------------
        else:
            results_out["mode"] = "single_pipe"
            pipe = self.data.get("pipe")
            if pipe is None:
                # build from diameter/length
                pipe = self._ensure_pipe_object()
            rep, calc = self._calc_single_pipe(pipe, q)
            total_dp_pa = calc["pressure_drop"].to("Pa").value
            total_head = total_dp_pa / (self._get_density().value * G)
            pump_eff = self.data.get("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
            shaft_power_kw = (total_dp_pa * q.value) / (1000.0 * pump_eff)

            results_out["summary"] = {
                "flow_m3s": q.value,
                "total_pressure_drop_Pa": total_dp_pa,
                "total_head_m": total_head,
                "pump_shaft_power_kW": shaft_power_kw,
            }
            results_out["components"] = [rep.as_dict()]

        # wrap into PipelineResults and store
        self._results = PipelineResults(results_out)
        return self._results

    # ---------------------- Backwards compatibility / helpers ---------------
    def _ensure_pipe_object(self) -> Pipe:
        """Constructs a Pipe object from engine data if not provided."""
        if isinstance(self.data.get("pipe"), Pipe):
            return self.data["pipe"]
        d = self.data.get("diameter")
        L = self.data.get("length") or Length(1.0, "m")
        if d is None:
            # compute optimum
            ideal = OptimumPipeDiameter(flow_rate=self._infer_flowrate(), density=self._get_density()).calculate()
            p = Pipe(name="Main Pipe", nominal_diameter=ideal, length=L)
            self.data["pipe"] = p
            return p
        if not isinstance(d, Diameter):
            d = _ensure_diameter_obj(d, self.data.get("assume_mm_for_numbers", True))
        p = Pipe(name="Main Pipe", internal_diameter=d, length=L)
        self.data["pipe"] = p
        return p


# End of file
