# processpi/pipelines/engine.py

from typing import Dict, Any, Optional, List, Tuple, Union

from .standards import get_nearest_diameter
from ..components import Component
from ..units import VolumetricFlowRate, Pressure
from ..calculations.fluids import (
    ReynoldsNumber,
    ColebrookWhite,
    OptimumPipeDiameter,
    PressureDropDarcy,
    FluidVelocity,
)
from .pipes import Pipe
from .fittings import Fitting
from .network import PipelineNetwork


Number = Union[int, float]


class PipelineEngine:
    """
    Flexible pipeline hydraulics engine with automatic dependency resolution.
    Works for a single pipe OR a PipelineNetwork (series/parallel).

    Inputs (any subset; engine infers the rest):
        flowrate: VolumetricFlowRate or float [m^3/s]
        fluid: Component
        density: float [kg/m^3]
        viscosity: float [Pa·s]
        length: float [m] (used for single-pipe mode or when building Pipe)
        diameter: float [m] (if given, engine builds a Pipe with this dia)
        material: str (default 'CS')
        schedule: str (default '40')
        pipe: Pipe
        network: PipelineNetwork
        flow_split: dict  (only for parallel subnetworks)
            - key: subnetwork.name
            - value: list of fractions (sum≈1) OR list of absolute flows [m^3/s]
              applied in the order of branches inside that parallel subnetwork.

    Returns from run():
        - If single pipe: diameter, velocity, Re, pressure_drop
        - If network: per-pipe results, per-branch summaries, totals, schematic
    """

    def __init__(self, **kwargs: Any):
        self.data: Dict[str, Any] = kwargs.copy()
        # cache of last velocity within a series chain to evaluate fitting K-losses
        self._last_series_velocity: Optional[float] = None

    # -------------------- Unit helpers --------------------

    def _get_flowrate(self) -> float:
        if "flowrate" in self.data:
            q = self.data["flowrate"]
            if isinstance(q, VolumetricFlowRate):
                return q.to("m3/s").value if hasattr(q.to("m3/s"), "value") else q.to("m3/s")
            return float(q)  # assume already m3/s
        raise ValueError("flowrate is required (at least at the network/entry level).")

    def _get_density(self) -> float:
        if "density" in self.data:
            return float(self.data["density"])
        if "fluid" in self.data and isinstance(self.data["fluid"], Component):
            return float(self.data["fluid"].density())
        raise ValueError("Provide density or a fluid Component.")

    def _get_viscosity(self) -> float:
        if "viscosity" in self.data:
            return float(self.data["viscosity"])
        if "fluid" in self.data and isinstance(self.data["fluid"], Component):
            return float(self.data["fluid"].viscosity())
        raise ValueError("Provide viscosity or a fluid Component.")

    def _ensure_pipe(self) -> Pipe:
        """Return a Pipe object, creating/optimizing if needed (single-pipe mode)."""
        if "pipe" in self.data and isinstance(self.data["pipe"], Pipe):
            return self.data["pipe"]

        # If a diameter is provided, build a pipe
        if "diameter" in self.data:
            pipe = Pipe(
                nominal_diameter=self.data["diameter"],  # meters expected
                schedule=self.data.get("schedule", "40"),
                material=self.data.get("material", "CS"),
                length=self.data.get("length", 1.0),
            )
            self.data["pipe"] = pipe
            return pipe

        # Otherwise, optimize diameter if we have flowrate & density
        if "flowrate" in self.data:
            opt = OptimumPipeDiameter(
                flow_rate=self._as_flowrate(self.data["flowrate"]),
                density=self._get_density(),
            )
            dia_opt = opt.calculate()  # meters (Dimension: Length)
            dia_sel = get_nearest_diameter(dia_opt)
            pipe = Pipe(
                nominal_diameter=dia_sel,
                schedule=self.data.get("schedule", "40"),
                material=self.data.get("material", "CS"),
                length=self.data.get("length", 1.0),
            )
            self.data["pipe"] = pipe
            return pipe

        raise ValueError("Cannot build pipe: need (pipe) or (diameter) or (flowrate+density).")

    def _as_flowrate(self, q: Union[VolumetricFlowRate, Number]) -> VolumetricFlowRate:
        if isinstance(q, VolumetricFlowRate):
            return q.to("m3/s")
        return VolumetricFlowRate(float(q), "m3/s")

    # -------------------- Core calcs for a pipe --------------------

    def _internal_diameter_m(self, pipe: Pipe) -> float:
        # Prefer the pipe's internal_diameter() if present (returns mm in your code)
        if hasattr(pipe, "internal_diameter"):
            di_mm = pipe.internal_diameter()
            return float(di_mm) / 1000.0
        # Else assume nominal_diameter is meters
        return float(pipe.nominal_diameter)

    def _velocity(self, q_m3s: float, pipe: Pipe) -> float:
        # Use your FluidVelocity class (expects diameter in m)
        D = self._internal_diameter_m(pipe)
        vel_calc = FluidVelocity(
            volumetric_flow_rate=self._as_flowrate(q_m3s),
            diameter=D,
        )
        return float(vel_calc.calculate())

    def _reynolds(self, v: float, pipe: Pipe) -> float:
        re_calc = ReynoldsNumber(
            density=self._get_density(),
            velocity=v,
            diameter=self._internal_diameter_m(pipe),
            viscosity=self._get_viscosity(),
        )
        return float(re_calc.calculate())

    def _friction_factor(self, Re: float, pipe: Pipe) -> float:
        # Your standards store roughness in mm; convert to m
        eps_m = float(pipe.roughness) / 1000.0 if pipe.roughness > 1e-5 else float(pipe.roughness)
        f_calc = ColebrookWhite(
            reynolds_number=Re,
            roughness=eps_m,
            diameter=self._internal_diameter_m(pipe),
        )
        return float(f_calc.calculate())

    def _major_loss_dp(self, f: float, v: float, pipe: Pipe) -> float:
        dp_calc = PressureDropDarcy(
            friction_factor=f,
            length=float(pipe.length),
            diameter=self._internal_diameter_m(pipe),
            density=self._get_density(),
            velocity=v,
        )
        return float(dp_calc.calculate())

    def _minor_loss_dp(self, K: float, v: float) -> float:
        rho = self._get_density()
        return float(K) * 0.5 * rho * (v ** 2)

    # -------------------- Network evaluation --------------------

    def _compute_series(self, elements: List[Any], q_m3s: float) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Compute ΔP across a series list of elements at flow q_m3s.
        Returns (dp_total, pipe_results[]).
        """
        results: List[Dict[str, Any]] = []
        dp_total = 0.0
        last_v: Optional[float] = None

        for e in elements:
            if isinstance(e, Pipe):
                v = self._velocity(q_m3s, e)
                Re = self._reynolds(v, e)
                f = self._friction_factor(Re, e)
                dp = self._major_loss_dp(f, v, e)

                results.append({
                    "type": "pipe",
                    "name": getattr(e, "name", f"{getattr(e, 'start_node', None) and getattr(e.start_node, 'name', '?')}→{getattr(e, 'end_node', None) and getattr(e.end_node, 'name', '?')}"),
                    "diameter_m": self._internal_diameter_m(e),
                    "velocity_m_s": v,
                    "reynolds_number": Re,
                    "friction_factor": f,
                    "pressure_drop_Pa": dp,
                })
                dp_total += dp
                last_v = v

            elif isinstance(e, Fitting):
                # Use last known velocity in this series leg
                if last_v is None:
                    # If we have no upstream pipe yet, we cannot compute; record None
                    results.append({
                        "type": "fitting",
                        "name": getattr(e, "fitting_type", "fitting"),
                        "K": e.K,
                        "pressure_drop_Pa": None,
                        "note": "No upstream velocity available to compute K-loss",
                    })
                else:
                    dp_k = self._minor_loss_dp(e.K, last_v)
                    results.append({
                        "type": "fitting",
                        "name": getattr(e, "fitting_type", "fitting"),
                        "K": e.K,
                        "pressure_drop_Pa": dp_k,
                    })
                    dp_total += dp_k

            elif isinstance(e, PipelineNetwork):
                # Recurse: for a series subnetwork, same flow passes through
                dp_sub, sub_pipes, sub_branches = self._compute_network(e, q_m3s)
                results.extend(sub_pipes)
                dp_total += dp_sub

        return dp_total, results

    def _resolve_parallel_flows(self, net: PipelineNetwork, q_m3s: float, branches: List[Any]) -> List[float]:
        """
        Determine branch flows for a parallel subnetwork named net.name.
        Uses self.data["flow_split"]. If absent: equal split across branches.
        flow_split[net.name] may be fractions summing to ~1 or absolute flows.
        """
        n = len(branches)
        split_cfg = (self.data.get("flow_split") or {}).get(net.name)

        if split_cfg is None:
            # Equal split
            return [q_m3s / n] * n

        # Try as absolute flows
        vals = [float(x) for x in split_cfg]
        if sum(vals) > 1.5 * q_m3s:  # clearly not fractions
            return vals

        # Treat as fractions, normalize a bit
        s = sum(vals)
        if s <= 0:
            return [q_m3s / n] * n
        return [q_m3s * (v / s) for v in vals]

    def _compute_network(self, net: PipelineNetwork, q_m3s: float) -> Tuple[float, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Evaluate a PipelineNetwork at an inlet flow q_m3s.
        Returns:
            total_dp,
            pipe_results (flat list),
            branch_summaries (for parallel sections)
        """
        if net.connection_type in (None, "series"):
            dp, pipes = self._compute_series(net.elements, q_m3s)
            return dp, pipes, []

        # Parallel network: treat each direct child element as a branch.
        branches = net.elements[:]
        q_branches = self._resolve_parallel_flows(net, q_m3s, branches)

        branch_summaries: List[Dict[str, Any]] = []
        dp_across = 0.0   # ΔP across the parallel block (use max of branches)
        all_pipe_results: List[Dict[str, Any]] = []

        for idx, (child, qb) in enumerate(zip(branches, q_branches), start=1):
            # Wrap non-network child into a temporary series list
            if isinstance(child, PipelineNetwork):
                # If child is itself parallel/series, recurse with flow qb
                dp_b, pipes_b, sub_branches = self._compute_network(child, qb)
                all_pipe_results.extend(pipes_b)
                branch_summaries.extend(sub_branches)
            else:
                # Child is a Pipe or Fitting; build a series list with possibly only that element
                dp_b, pipes_b = self._compute_series([child], qb)
                all_pipe_results.extend(pipes_b)

            # Compute dp for this branch alone
            # If child was a fitting alone, dp_b may be 0 or None; handle robustly
            dp_branch = 0.0
            for r in all_pipe_results[-len(pipes_b):] if pipes_b else []:
                if r.get("pressure_drop_Pa") is not None:
                    dp_branch += float(r["pressure_drop_Pa"])

            branch_summaries.append({
                "parallel_name": net.name,
                "branch_index": idx,
                "flow_m3_s": qb,
                "pressure_drop_Pa": dp_b if dp_b is not None else dp_branch,
            })

            dp_across = max(dp_across, dp_b)

        return dp_across, all_pipe_results, branch_summaries

    # -------------------- Public API --------------------

    def run(self) -> Dict[str, Any]:
        """
        Execute calculations based on provided inputs.
        - If a network is provided: compute per-pipe/branch and totals.
        - Else: single-pipe mode with auto dependency resolution.
        """
        results: Dict[str, Any] = {}

        # NETWORK MODE
        if "network" in self.data and isinstance(self.data["network"], PipelineNetwork):
            net: PipelineNetwork = self.data["network"]
            q_in = self._get_flowrate()

            total_dp, pipe_results, branch_summaries = self._compute_network(net, q_in)

            results["mode"] = "network"
            results["summary"] = {
                "inlet_flow_m3_s": q_in,
                "total_pressure_drop_Pa": total_dp,
            }
            results["pipes"] = pipe_results
            if branch_summaries:
                results["parallel_sections"] = branch_summaries
            # include schematic
            if hasattr(net, "schematic"):
                results["schematic"] = net.schematic()
            return results

        # SINGLE PIPE MODE
        pipe = self._ensure_pipe()
        q_m3s = self._get_flowrate()

        D_m = self._internal_diameter_m(pipe)
        v = self._velocity(q_m3s, pipe)
        Re = self._reynolds(v, pipe)
        f = self._friction_factor(Re, pipe)
        dp = self._major_loss_dp(f, v, pipe)

        results["mode"] = "single"
        results["pipe"] = {
            "diameter_m": D_m,
            "diameter_in": getattr(pipe.nominal_diameter, "to", lambda u: D_m)(  # if units class exists
                "in"
            ) if hasattr(pipe.nominal_diameter, "to") else None,
            "material": getattr(pipe, "material", None),
            "schedule": getattr(pipe, "schedule", None),
            "length_m": float(getattr(pipe, "length", 0.0)),
        }
        results["velocity_m_s"] = v
        results["reynolds_number"] = Re
        results["friction_factor"] = f
        results["pressure_drop_Pa"] = dp
        return results
