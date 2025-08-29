# processpi/pipelines/engine.py
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
    FluidVelocity, ReynoldsNumber, PressureDropDarcy, OptimumPipeDiameter, PressureDropFanning, ColebrookWhite, PressureDropHazenWilliams
)


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
    elevation_dp_pa: Optional[float] = None
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
            "elevation_loss_Pa": self.elevation_dp_pa,
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
        """Configure engine inputs. Converts and normalizes keys/aliases."""
        self.data = dict(kwargs)

        # Aliases
        alias_map = {
            "flowrate": ["flow_rate", "q", "Q","flowrate"],
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
        self.data.setdefault("method", "darcy_weisbach")
        self.data.setdefault("hw_coefficient", 130.0)
        self.data.setdefault("solver", "auto")

        # Validate network type
        net = self.data.get("network")
        if net is not None and not isinstance(net, PipelineNetwork):
            raise TypeError("`network` must be a PipelineNetwork instance.")

        # Explicitly bind normalized attributes for internal use
        self.flowrate = self.data.get("flowrate")
        self.diameter = self.data.get("diameter")
        self.velocity = self.data.get("velocity")
        #self.internal_diameter = self.data.get("internal_diameter")
        self.mass_flowrate = self.data.get("mass_flowrate")
        # print(self)

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
    
    def _maybe_velocity(self, pipe):
        """
        Ensures velocity is available. If not explicitly provided, 
        calculates velocity using volumetric flow rate and pipe diameter.
        """
        if hasattr(pipe, "velocity") and pipe.velocity is not None:
            return pipe.velocity
        elif hasattr(pipe, "flow_rate") and hasattr(pipe, "diameter"):
            area = math.pi * (pipe.diameter.value ** 2) / 4.0
            velocity_value = pipe.flow_rate.value / area
            return Velocity(velocity_value, pipe.flow_rate.unit + "/" + pipe.diameter.unit)
        else:
            raise ValueError(
                "Insufficient data: cannot calculate velocity without diameter and flow rate."
            )


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
            print(d)
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

    # ---------------------- Pipe calculation (major+minor+elevation) ---------
    def _pipe_calculation(self, pipe: Pipe, flow_rate: Optional[VolumetricFlowRate]) -> Dict[str, Any]:
        """
        Calculates fluid dynamics and pressure drop for a single pipe.
        Includes:
         - frictional (Darcy or Hazen-Williams),
         - minor losses (K or Le),
         - elevation (rho * g * delta_h).
        """
        # Determine velocity: use fixed velocity from engine or compute it.
        v = self.data.get("velocity")
        if v is None:
            q = flow_rate or self._infer_flowrate()
            v = FluidVelocity(volumetric_flow_rate=q, diameter=self._resolve_internal_diameter(pipe)).calculate()
        else:
            if not isinstance(v, Velocity):
                v = Velocity(float(v), "m/s")

        # Flowrate
        q_used = flow_rate or self._infer_flowrate()

        # Friction / Reynolds / f
        Re = self._reynolds(v, pipe.internal_diameter or self._resolve_internal_diameter(pipe))
        material = getattr(pipe, "material", None)
        f = None
        method = self.data.get("method", "darcy_weisbach").lower()

        if method == "hazen_williams":
            # Hazen-Williams: calculate using provided module/class
            hw_coeff = getattr(pipe, "hw_coefficient", None) or self.data.get("hw_coefficient", 130.0)
            hw_calc = PressureDropHazenWilliams(
                inputs={
                    "length": pipe.length or Length(1.0, "m"),
                    "flow_rate": q_used,
                    "coefficient": hw_coeff,
                    "diameter": self._resolve_internal_diameter(pipe),
                    "density": self._get_density(),
                }
            )
            dp_major = hw_calc.calculate()
            # f left as None because HW does not directly yield Darcy f
            f = None
        else:
            # Darcy–Weisbach path
            f = self._friction_factor(Re, self._resolve_internal_diameter(pipe), material)
            dp_major = self._major_dp_pa(f, pipe.length or Length(1.0, "m"), self._resolve_internal_diameter(pipe), v)

        # Minor losses
        dp_minor = Pressure(0.0, "Pa")
        d = self._resolve_internal_diameter(pipe)
        fittings: List[Fitting] = []
        if hasattr(pipe, "fittings") and isinstance(pipe.fittings, list):
            fittings = pipe.fittings
        elif "network" not in self.data and isinstance(self.data.get("fittings"), list):
            # In single-pipe mode, fittings can be passed at the top level.
            fittings = self.data["fittings"]

        for ft in fittings:
            dp_minor += self._minor_dp_pa(ft, v, f, d)

        # Elevation loss/gain: if nodes available on the pipe
        elev_loss = Pressure(0.0, "Pa")
        rho_val = self._get_density().value
        start_node = getattr(pipe, "start_node", None)
        end_node = getattr(pipe, "end_node", None)
        if start_node is not None and end_node is not None:
            try:
                elev_diff_m = float(getattr(end_node, "elevation", 0.0)) - float(getattr(start_node, "elevation", 0.0))
                elev_loss = Pressure(rho_val * G * elev_diff_m, "Pa")
            except Exception:
                elev_loss = Pressure(0.0, "Pa")

        total_dp_pa = dp_major.to("Pa").value + dp_minor.to("Pa").value + elev_loss.to("Pa").value

        return {
            "velocity": v,
            "reynolds": Re,
            "friction_factor": f,
            "major_dp": dp_major,
            "minor_dp": dp_minor,
            "elevation_dp": elev_loss,
            "pressure_drop": Pressure(total_dp_pa, "Pa"),
            "major_dp_pa": dp_major.to("Pa").value,
            "minor_dp_pa": dp_minor.to("Pa").value,
            "elevation_dp_pa": elev_loss.to("Pa").value,
        }

    # ---------------------- Series/Parallel evaluation -------------------------

    def _compute_series(self, series_list: List[Any], flow_rate: VolumetricFlowRate, fluid: Any) -> Tuple[Pressure, List[Dict[str, Any]]]:
        """
        Calculates the total pressure drop and results for a series of elements.
        """
        results = []
        dp_total = Pressure(0, "Pa")

        # Track velocity, diameter, and friction factor to pass to subsequent fittings.
        current_d: Optional[Diameter] = None
        current_v: Optional[Velocity] = None
        current_f: Optional[float] = None

        for element in series_list:
            # Generate a name for the element for the results.
            element_name = getattr(element, "name", getattr(element, "fitting_type", element.__class__.__name__.lower()))

            # --- Handle different element types ---

            # Pipe
            if isinstance(element, Pipe):
                calc = self._pipe_calculation(element, flow_rate)
                dp_total = Pressure(dp_total.to("Pa").value + calc["pressure_drop"].to("Pa").value, "Pa")
                current_d = self._internal_diameter_m(element)
                current_v = calc["velocity"]
                current_f = calc["friction_factor"]

                results.append({
                    "type": "pipe",
                    "name": element_name,
                    "length": element.length,
                    "diameter": current_d,
                    "pressure_drop_Pa": calc["pressure_drop"].to("Pa").value,
                    "major_dp_Pa": calc.get("major_dp_pa"),
                    "minor_dp_Pa": calc.get("minor_dp_pa"),
                    "elevation_dp_Pa": calc.get("elevation_dp_pa"),
                    "reynolds": calc["reynolds"],
                    "friction_factor": current_f,
                    "velocity": current_v,
                })

            # Pump (energy gain)
            elif element.__class__.__name__ == "Pump":
                pump_gain = self._pump_gain_pa(element)
                dp_total = Pressure(dp_total.to("Pa").value - pump_gain.to("Pa").value, "Pa")
                results.append({
                    "type": "pump",
                    "name": element_name,
                    "head_gain_Pa": pump_gain.to("Pa").value if isinstance(pump_gain, Pressure) else float(pump_gain),
                    "head_m": getattr(element, "head", None),
                    "efficiency": getattr(element, "efficiency", None),
                })

            # Equipment (e.g., heat exchanger, valve)
            elif element.__class__.__name__ == "Equipment":
                eq_dp = self._equipment_dp_pa(element)
                dp_total = Pressure(dp_total.to("Pa").value + eq_dp.to("Pa").value, "Pa")
                results.append({
                    "type": "equipment",
                    "name": getattr(element, "name", element_name),
                    "pressure_drop_Pa": eq_dp.to("Pa").value,
                })

            # Fitting (minor loss)
            elif isinstance(element, Fitting):
                if current_d is None or current_v is None:
                    # If we encounter a fitting before a pipe, infer velocity/diameter
                    # from the main engine inputs.
                    d_for_fit = getattr(element, "diameter", self._internal_diameter_m())
                    q = flow_rate or self._infer_flowrate()
                    current_v = FluidVelocity(volumetric_flow_rate=q, diameter=d_for_fit).calculate()
                    current_d = d_for_fit
                    current_f = None

                dp_fit = self._fitting_dp_pa(element, current_v, current_f, current_d)
                dp_total = Pressure(dp_total.to("Pa").value + dp_fit.to("Pa").value, "Pa")
                results.append({
                    "type": "fitting",
                    "name": element_name,
                    "pressure_drop_Pa": dp_fit.to("Pa").value,
                    "using": "K" if hasattr(element, "K") and element.K is not None else ("Le" if hasattr(element, "Le") and element.Le is not None else "none"),
                    "quantity": getattr(element, "quantity", 1),
                })

            # Vessel (boundary or holding element with no pressure drop by default)
            elif element.__class__.__name__ == "Vessel":
                results.append({
                    "type": "vessel",
                    "name": getattr(element, "name", element_name),
                    "pressure_drop_Pa": Pressure(0.0, "Pa"),
                    "note": "No default ΔP; boundary/holdup element.",
                })

            # Nested Networks (this path shouldn't be reached as it's handled in _compute_network)
            elif isinstance(element, PipelineNetwork):
                raise TypeError("Nested networks should be handled in _compute_network, not _compute_series.")

            else:
                raise TypeError(f"Unsupported element type: {type(element).__name__}")

            # Optional: Check for inlet/outlet pressures defined on the element itself.
            inlet_p = getattr(element, "inlet_pressure", None)
            outlet_p = getattr(element, "outlet_pressure", None)
            if inlet_p is not None and outlet_p is not None:
                dp_element = self._as_pressure(inlet_p).to("Pa") - self._as_pressure(outlet_p).to("Pa")
                dp_total = Pressure(dp_total.to("Pa").value + dp_element, "Pa")
                results[-1].update({
                    "inlet_pressure_Pa": self._as_pressure(inlet_p).to("Pa"),
                    "outlet_pressure_Pa": self._as_pressure(outlet_p).to("Pa"),
                    "net_dp_from_defined_pressures_Pa": dp_element
                })

        return dp_total, results

    def _resolve_parallel_flows(self, net: PipelineNetwork, q_m3s: VolumetricFlowRate, branches: List[Any]) -> List[float]:
        """
        Determines the flow rate for each branch in a parallel network.
        This can be based on a user-provided split ratio or a simple equal split.
        """
        split_cfg = (self.data.get("flow_split") or {}).get(net.name)
        n = len(branches)
        if split_cfg is None:
            # Default to equal flow split if no configuration is provided.
            return [q_m3s.value / n] * n

        vals = [float(x) for x in split_cfg]
        # Heuristic: if sum of values is much greater than total flow, treat as absolute flows.
        if sum(vals) > 1.5 * q_m3s.value:
            return vals

        # Otherwise, treat as ratios.
        s = sum(vals)
        return [q_m3s.value * (v / s) for v in vals]

    # ---------------------- Network Solvers ---------------------------------
    def _hardy_cross(self, network: PipelineNetwork, q_total: VolumetricFlowRate, tol: float) -> Tuple[bool, float, List[ElementReport]]:
        """Hardy-Cross iterative solver for a parallel/looped network.

        Strategy:
        - For a top-level parallel group, assign initial equal flows.
        - Iterate: compute heads for each branch (using _compute_network), approximate derivative dH/dQ,
          compute ΔQ correction and apply.
        - Collect element reports and return residual.
        """
        # Get parallel branches for this network block
        branches = network.get_parallel_branches() if hasattr(network, "get_parallel_branches") else getattr(network, "elements", [])
        # If not a parallel block, fallback to single-branch result
        if not branches:
            # compute whole network as series
            dp, el_reports, branch_reports = self._compute_network(network, q_total)
            reports = [ElementReport(name=r.get("name", "el"), type=r.get("type", "el"), dp_pa=r.get("pressure_drop_Pa")) for r in el_reports]
            return True, 0.0, reports

        n = len(branches)
        branch_flows = [q_total.value / n] * n

        for it in range(MAX_HC_ITER):
            max_residual = 0.0
            reports: List[ElementReport] = []
            for i, branch in enumerate(branches):
                q_b = VolumetricFlowRate(branch_flows[i], "m3/s")
                dp_branch, el_reports, _ = self._compute_network(branch, q_b)
                # convert to head (m)
                H = dp_branch.to("Pa").value / (self._get_density().value * G)
                # derivative estimate dH/dQ ≈ n * H / Q  (heuristic better than 2*H/Q in mixed networks)
                if abs(q_b.value) < 1e-12:
                    dHdQ = 1e12
                else:
                    dHdQ = 2.0 * H / q_b.value
                dq = -H / dHdQ
                branch_flows[i] += dq
                max_residual = max(max_residual, abs(dq))
                # collect element reports
                for r in el_reports:
                    rep = ElementReport(
                        name=r.get("name", "element"),
                        type=r.get("type", "element"),
                        diameter_m=(r.get("diameter").to("m").value if isinstance(r.get("diameter"), Diameter) else None),
                        flow_m3s=float(q_b.value),
                        velocity_m_s=(r.get("velocity").value if hasattr(r.get("velocity"), "value") else None),
                        reynolds=r.get("reynolds"),
                        friction_factor=r.get("friction_factor"),
                        dp_pa=r.get("pressure_drop_Pa"),
                        elevation_dp_pa=r.get("elevation_dp_Pa"),
                        head_m=(dp_branch.to("Pa").value / (self._get_density().value * G)),
                        warnings=[]
                    )
                    reports.append(rep)
            if max_residual < tol:
                return True, max_residual, reports
        return False, max_residual, reports

    def _matrix_solver(self, network: PipelineNetwork, q_total: VolumetricFlowRate, tol: float) -> Tuple[bool, float, List[ElementReport]]:
        """Simple matrix-style solver for distributing flows in parallel groups.

        This is a Picard-like scheme:
        - Initialize branch flows.
        - Compute H_i for each branch using _compute_network.
        - Update branch flows proportionally to 1/H_i (so branches with lower head take more flow).
        - Repeat until flow adjustments are small.
        """
        branches = network.get_parallel_branches() if hasattr(network, "get_parallel_branches") else getattr(network, "elements", [])
        if not branches:
            dp, el_reports, branch_reports = self._compute_network(network, q_total)
            reports = [ElementReport(name=r.get("name", "el"), type=r.get("type", "el"), dp_pa=r.get("pressure_drop_Pa")) for r in el_reports]
            return True, 0.0, reports

        n = len(branches)
        branch_flows = [q_total.value / n] * n

        for it in range(MAX_MATRIX_ITER):
            prev = branch_flows.copy()
            reports: List[ElementReport] = []
            heads = []
            for i, branch in enumerate(branches):
                q_b = VolumetricFlowRate(branch_flows[i], "m3/s")
                dp_branch, el_reports, _ = self._compute_network(branch, q_b)
                H = dp_branch.to("Pa").value / (self._get_density().value * G)
                heads.append(H)
                # collect per-branch element reports
                for r in el_reports:
                    rep = ElementReport(
                        name=r.get("name", "element"),
                        type=r.get("type", "element"),
                        diameter_m=(r.get("diameter").to("m").value if isinstance(r.get("diameter"), Diameter) else None),
                        flow_m3s=float(q_b.value),
                        velocity_m_s=(r.get("velocity").value if hasattr(r.get("velocity"), "value") else None),
                        reynolds=r.get("reynolds"),
                        friction_factor=r.get("friction_factor"),
                        dp_pa=r.get("pressure_drop_Pa"),
                        elevation_dp_pa=r.get("elevation_dp_Pa"),
                        head_m=H,
                        warnings=[]
                    )
                    reports.append(rep)
            if sum(heads) == 0:
                break
            inv = [1.0 / max(h, 1e-12) for h in heads]
            s = sum(inv)
            for i in range(n):
                branch_flows[i] = q_total.value * (inv[i] / s)
            max_change = max(abs(branch_flows[i] - prev[i]) for i in range(n))
            if max_change < tol:
                return True, max_change, reports
        return False, max_change, reports

    # ---------------------- Network wrapper (choose solver) ------------------
    def _solve_network_dual(self, network: PipelineNetwork, q_total: VolumetricFlowRate, tol: float) -> Dict[str, Any]:
        """Run both matrix solver and Hardy-Cross (or selected solver); compare residuals and return best."""
        preferred = self.data.get("solver", "auto").lower()
        # If user requested a specific solver, run only that.
        if preferred == "matrix":
            matrix_ok, matrix_res, matrix_reports = self._matrix_solver(network, q_total, tol)
            return {"method": "matrix", "converged": matrix_ok, "residual": matrix_res, "reports": matrix_reports}
        if preferred == "hardy_cross":
            hc_ok, hc_res, hc_reports = self._hardy_cross(network, q_total, tol)
            return {"method": "hardy_cross", "converged": hc_ok, "residual": hc_res, "reports": hc_reports}

        # Auto: run both and pick smaller residual
        matrix_ok, matrix_res, matrix_reports = self._matrix_solver(network, q_total, tol)
        hc_ok, hc_res, hc_reports = self._hardy_cross(network, q_total, tol)

        if matrix_res <= hc_res:
            return {"method": "matrix", "converged": matrix_ok, "residual": matrix_res, "reports": matrix_reports}
        else:
            return {"method": "hardy_cross", "converged": hc_ok, "residual": hc_res, "reports": hc_reports}

    # ---------------------- Diameter selection -------------------------------
    def _select_standard_diameter(self, ideal_d_m: float) -> Tuple[str, Diameter]:
        """Map a continuous ideal diameter (m) to nearest standard nominal and return (nominal_label, Diameter).
        Picks the smallest standard size that yields diameter >= ideal.
        """
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
        candidates.sort(key=lambda x: x[1].to("m").value)
        for label, d in candidates:
            if d.to("m").value >= ideal_d_m:
                return label, d
        if candidates:
            return candidates[-1][0], candidates[-1][1]
        raise ValueError("No standard pipe diameters available in catalog")

    # ---------------------- Utility helpers ---------------------------------
    def _as_pressure(self, maybe_pressure: Any, default_unit: str = "Pa") -> Optional[Pressure]:
        if maybe_pressure is None:
            return None
        if isinstance(maybe_pressure, Pressure):
            return maybe_pressure
        return Pressure(float(maybe_pressure), default_unit)

    def _pump_gain_pa(self, pump: Any) -> Pressure:
        """Convert pump object head/pressure to Pa. Accepts `head` (m) or inlet/outlet pressures."""
        rho = getattr(pump, "density", None) or self._get_density().value
        pin = getattr(pump, "inlet_pressure", None)
        pout = getattr(pump, "outlet_pressure", None)
        if pin is not None and pout is not None:
            return self._as_pressure(pout).to("Pa") - self._as_pressure(pin).to("Pa")
        head = getattr(pump, "head", None)
        if head is not None:
            return Pressure(rho * G * float(head), "Pa")
        return Pressure(0.0, "Pa")

    def _equipment_dp_pa(self, eq: Any) -> Pressure:
        """Converts Equipment pressure_drop (assumed bar) to Pa if needed."""
        dp = getattr(eq, "pressure_drop", 0.0) or 0.0
        return Pressure(float(dp), "bar").to("Pa") if not isinstance(dp, Pressure) else dp

    def _fitting_dp_pa(self, fitting: Fitting, v: Velocity, f: Optional[float], d: Diameter) -> Pressure:
        """Compute fitting pressure drop using K or Le approaches."""
        rho = self._get_density().value
        v_val = v.value if hasattr(v, "value") else float(v)
        K = getattr(fitting, "K", None) or getattr(fitting, "K_factor", None) or getattr(fitting, "total_K", None)
        if K is not None:
            try:
                return Pressure(0.5 * rho * v_val * v_val * float(K), "Pa")
            except (TypeError, ValueError):
                pass
        Le = getattr(fitting, "Le", None) or getattr(fitting, "equivalent_length", None)
        if Le is not None:
            if f is None:
                Re = self._reynolds(v, d)
                f_val = self._friction_factor(Re, d)
            else:
                f_val = float(f)
            d_m = d.to("m").value
            return Pressure(float(f_val) * (float(Le) / d_m) * 0.5 * rho * v_val * v_val, "Pa")
        return Pressure(0.0, "Pa")

    # -------------------- RUN / SUMMARY --------------------------------------

    def run(self) -> PipelineResults:
        """Execute configured simulation or sizing job and return PipelineResults."""
        net = self.data.get("network")
        pipe = self.data.get("pipe")
        diameter = self.data.get("diameter")
        available_dp = self.data.get("available_dp")
        rho = self._get_density().value
        q_in = self._infer_flowrate()
        tol = self.data.get("tolerance_m3s", DEFAULT_FLOW_TOL)

        results_out: Dict[str, Any] = {"mode": None, "summary": {}, "components": []}

        # -------------------- Network mode --------------------
        if isinstance(net, PipelineNetwork):
            # Size any missing diameters using _solve_for_diameter logic
            for p in net.get_all_pipes():
                if p.nominal_diameter is None:
                    # Assign flow to branch
                    q_branch = q_in / len(net.get_all_pipes()) if len(net.get_all_pipes()) else q_in
                    # Solve for diameter based on velocity ± available_dp
                    self.data.update({
                        "pipe": p,
                        "fluid": self.data.get("fluid"),
                        "available_dp": available_dp,
                    })
                    res = self._solve_for_diameter(**self.data)
                    p.nominal_diameter = res.components[0]["diameter"]

            # Solve network with dual method
            solved = self._solve_network_dual(net, q_in, tol)
            reports = solved.get("reports", [])
            comp_list = [r.as_dict() for r in reports]

            total_dp_pa = sum(float(r.get("pressure_drop_Pa", 0.0)) for r in comp_list)
            total_elev_pa = sum(float(r.get("elevation_loss_Pa", 0.0)) for r in comp_list)
            total_head_m = total_dp_pa / (rho * G)
            pump_eff = self.data.get("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
            shaft_power_kw = (total_dp_pa * q_in.value) / (1000.0 * pump_eff)

            results_out["mode"] = "network"
            results_out["summary"] = {
                "inlet_flow_m3s": q_in.value,
                "total_pressure_drop_Pa": total_dp_pa,
                "total_elevation_Pa": total_elev_pa,
                "total_head_m": total_head_m,
                "pump_shaft_power_kW": shaft_power_kw,
                "solver_method": solved.get("method"),
                "solver_converged": solved.get("converged"),
                "solver_residual": solved.get("residual"),
            }
            results_out["components"] = comp_list

        # -------------------- Single pipe mode --------------------
        else:
            # If diameter provided, use it
            if diameter is not None:
                pipe_instance = self._ensure_pipe_object()
                pipe_instance.internal_diameter = diameter
                calc = self._pipe_calculation(pipe_instance, q_in)
                total_dp_pa = calc["pressure_drop"].to("Pa").value
                total_head = total_dp_pa / (rho * G)
                pump_eff = self.data.get("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
                shaft_power_kw = (total_dp_pa * q_in.value) / (1000.0 * pump_eff)

                results_out["mode"] = "single_pipe"
                results_out["summary"] = {
                    "flow_m3s": q_in.value,
                    "total_pressure_drop_Pa": total_dp_pa,
                    "total_head_m": total_head,
                    "pump_shaft_power_kW": shaft_power_kw,
                }
                results_out["components"] = [{
                    "type": "pipe",
                    "name": pipe_instance.name,
                    "length": pipe_instance.length,
                    "diameter": self._resolve_internal_diameter(pipe_instance),
                    "velocity": calc["velocity"],
                    "reynolds": calc["reynolds"],
                    "friction_factor": calc["friction_factor"],
                    "major_dp": calc["major_dp"],
                    "minor_dp": calc["minor_dp"],
                    "elevation_dp": calc["elevation_dp"],
                    "total_dp": calc["pressure_drop"],
                }]
            # If diameter missing → sizing required
            else:
                self.data.update({
                    "pipe": pipe,
                    "fluid": self.data.get("fluid"),
                    "available_dp": available_dp,
                })
                results_out = self._solve_for_diameter(**self.data).to_dict()

        # -------------------- Store and return --------------------
        self._results = PipelineResults(results_out)
        return self._results


    def summary(self) -> Optional[PipelineResults]:
        if not self._results:
            print("No results available for summary.")
            return None
        return self._results.summary()

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

# ---------------------- Diameter helper ---------------------------------
    def _resolve_internal_diameter(self, pipe: Pipe) -> Diameter:
        if pipe.internal_diameter:
            return pipe.internal_diameter
        if pipe.nominal_diameter:
            return pipe.nominal_diameter
        if self.diameter:
            return _ensure_diameter_obj(self.diameter)
        # fallback to optimum calculation
        opt_d = OptimumPipeDiameter(self._infer_flowrate(), self._get_density()).calculate()
        label, std_d = self._select_standard_diameter(opt_d.to("m").value)
        return Diameter(std_d, "m")

    def _select_standard_diameter(self, ideal_d_m: Diameter) -> Tuple[str, float]:
        # nearest standard nominal diameter
        standard_list = list_available_pipe_diameters()
        nearest = min(standard_list, key=lambda x: abs(x.value - ideal_d_m.value))
        label = f"{nearest} mm"
        return label, nearest
    
    #def _solve_for_diameter(self, **kwargs):
    def _solve_for_diameter(self, **kwargs):
        import math

        # --- Inputs ---
        fluid = kwargs.get("fluid") or self.data.get("fluid")
        flow_rate = self._infer_flowrate()
        available_dp = kwargs.get("available_dp") or self.data.get("available_dp")
        pump_eff = kwargs.get("pump_efficiency", 0.75)

        if not fluid or not flow_rate:
            raise ValueError("flow_rate and fluid are required for diameter sizing.")

        # --- Recommended velocity range (m/s) ---
        vel_range = get_recommended_velocity(fluid.name.strip().lower().replace(" ", "_"))
        if vel_range is None:
            v_min, v_max = 0.5, 100.0
        elif isinstance(vel_range, tuple):
            v_min, v_max = vel_range
        else:
            v_min = v_max = vel_range

        # --- Initial diameter guess using target velocity inside recommended range ---
        v_target = (v_min + v_max) / 2
        pipe_instance = self._ensure_pipe_object()
        D_final = math.sqrt(4 * flow_rate.value / (math.pi * v_target))
        pipe_instance.diameter = Diameter(D_final, "m")

        # --- Iterative convergence loop ---
        max_iterations = 30
        for iter_no in range(1, max_iterations + 1):
            calc = self._pipe_calculation(pipe_instance, flow_rate)
            v_calc = calc["velocity"].value if hasattr(calc["velocity"], "value") else calc["velocity"]
            total_dp_pa = calc["pressure_drop"].to("Pa").value

            # --- Diameter adjustment factor for velocity ---
            if v_calc < v_min:
                vel_factor = (v_calc / v_min) ** -0.5  # increase D
            elif v_calc > v_max:
                vel_factor = (v_calc / v_max) ** -0.5  # decrease D
            else:
                vel_factor = 1.0

            # --- Diameter adjustment factor for ΔP (if available) ---
            if available_dp:
                dp_target = available_dp.to("Pa").value
                dp_factor = (total_dp_pa / dp_target) ** 0.5
            else:
                dp_factor = 1.0

            # --- Combine factors to adjust diameter ---
            adjust_factor = max(vel_factor, dp_factor)
            D_final *= adjust_factor
            pipe_instance.diameter = Diameter(D_final, "m")

            # --- Logging ---
            print(
                f"Iteration {iter_no:02d}: D = {D_final:.5f} m | v_calc = {v_calc:.3f} m/s | "
                f"ΔP = {total_dp_pa:.2f} Pa | vel_factor = {vel_factor:.3f} | "
                f"dp_factor = {dp_factor:.3f} | adjust_factor = {adjust_factor:.3f}"
            )

            # --- Convergence check ---
            if abs(adjust_factor - 1.0) < 0.01 and v_min <= v_calc <= v_max:
                break

        # --- Final calculations ---
        calc = self._pipe_calculation(pipe_instance, flow_rate)
        total_dp_pa = calc["pressure_drop"].to("Pa").value
        rho = fluid.density().value
        G = 9.80665
        total_head = total_dp_pa / (rho * G)
        shaft_power_kw = (total_dp_pa * flow_rate.value) / (1000.0 * pump_eff)
        v_calc = calc["velocity"].value if hasattr(calc["velocity"], "value") else calc["velocity"]

        # --- Velocity warning ---
        if v_calc < v_min or v_calc > v_max:
            print(f"⚠️ Warning: Final velocity {v_calc:.2f} m/s is outside recommended range ({v_min:.2f}-{v_max:.2f} m/s) for {fluid.name}.")

        results_out = {
            "network_name": pipe_instance.name,
            "mode": "single_pipe",
            "summary": {
                "flow_m3s": flow_rate.value,
                "total_pressure_drop_Pa": total_dp_pa,
                "total_head_m": total_head,
                "pump_shaft_power_kW": shaft_power_kw,
                "velocity": v_calc,
                "reynolds": calc["reynolds"],
                "friction_factor": calc["friction_factor"],
                "calculated_diameter_m": D_final,
            },
            "components": [{
                "type": "pipe",
                "name": pipe_instance.name,
                "length": pipe_instance.length,
                "diameter": pipe_instance.diameter,
                "velocity": v_calc,
                "reynolds": calc["reynolds"],
                "friction_factor": calc["friction_factor"],
                "major_dp": calc["major_dp"],
                "minor_dp": calc["minor_dp"],
                "elevation_dp": calc["elevation_dp"],
                "total_dp": calc["pressure_drop"],
            }],
        }

        return PipelineResults(results_out)







    
    def _solve_for_diameter_network(self, network, **kwargs):
        """
        Iteratively size each pipe in the network based on flow, ΔP, and recommended velocity.
        Each pipe is sized sequentially; fittings and equipment are included in calculations.
        """
        import math

        fluid = kwargs.get("fluid") or self.data.get("fluid")
        if not fluid:
            raise ValueError("Fluid must be provided for diameter sizing.")

        RECOMMENDED_VELOCITIES = {
            "carbon_dioxide": (8.0, 15.0),
            "organic_liquids": (1.8, 2.0),
            "water": (1.0, 2.5),
            # Add more fluids as needed
        }
        fluid_type = fluid.name.lower()
        v_min, v_max = RECOMMENDED_VELOCITIES.get(fluid_type, (0.5, 100.0))

        # Loop over each pipe in the network
        all_results = []
        for pipe_instance in network.pipes:
            flow_rate = self._infer_flowrate(pipe_instance)
            available_dp = kwargs.get("available_dp") or None

            # Initial guess: target velocity
            v_target = (v_min + v_max) / 2
            D_final = math.sqrt(4 * flow_rate.value / (math.pi * v_target))
            pipe_instance.diameter = Diameter(D_final, "m")

            # Iterative convergence
            max_iterations = 20
            for i in range(max_iterations):
                calc = self._pipe_calculation(pipe_instance, flow_rate)
                total_dp_pa = calc["pressure_drop"].to("Pa").value
                v_calc = calc["velocity"]

                # ΔP adjustment
                dp_factor = (total_dp_pa / available_dp.to("Pa").value) ** 0.5 if available_dp else 1.0

                # Velocity adjustment
                vel_factor = 1.0
                if v_calc < v_min:
                    vel_factor = (v_calc / v_min) ** 0.5
                elif v_calc > v_max:
                    vel_factor = (v_calc / v_max) ** 0.5

                adjust_factor = max(dp_factor, vel_factor)
                if abs(adjust_factor - 1.0) < 0.01:
                    break  # converged

                D_final *= adjust_factor
                pipe_instance.diameter = Diameter(D_final, "m")

            # Velocity warning
            if v_calc < v_min or v_calc > v_max:
                print(
                    f"⚠️ Warning: Pipe '{pipe_instance.name}' velocity {v_calc:.2f} m/s "
                    f"outside recommended ({v_min}-{v_max}) m/s"
                )

            # Store results
            total_dp_pa = calc["pressure_drop"].to("Pa").value
            rho = fluid.density.value
            G = 9.80665
            total_head = total_dp_pa / (rho * G)
            pump_eff = kwargs.get("pump_efficiency", 0.75)
            shaft_power_kw = (total_dp_pa * flow_rate.value) / (1000.0 * pump_eff)

            all_results.append({
                "network_name": pipe_instance.name,
                "mode": "network_pipe",
                "summary": {
                    "flow_m3s": flow_rate.value,
                    "total_pressure_drop_Pa": total_dp_pa,
                    "total_head_m": total_head,
                    "pump_shaft_power_kW": shaft_power_kw,
                    "velocity": v_calc,
                    "reynolds": calc["reynolds"],
                    "friction_factor": calc["friction_factor"],
                    "calculated_diameter_m": D_final,
                },
                "components": [{
                    "type": "pipe",
                    "name": pipe_instance.name,
                    "length": pipe_instance.length,
                    "diameter": pipe_instance.diameter,
                    "velocity": calc["velocity"],
                    "reynolds": calc["reynolds"],
                    "friction_factor": calc["friction_factor"],
                    "major_dp": calc["major_dp"],
                    "minor_dp": calc["minor_dp"],
                    "elevation_dp": calc["elevation_dp"],
                    "total_dp": calc["pressure_drop"],
                }],
            })

        return PipelineResults({"all_simulation_results": all_results})


