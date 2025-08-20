# processpi/pipelines/engine.py

from typing import Dict, Any, Optional, List, Tuple, Union
from ..units import *

from ..components import Component
from ..calculations.fluids import (
    ReynoldsNumber,
    ColebrookWhite,
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
    """

    def __init__(self, **kwargs: Any):
        self.data: Dict[str, Any] = kwargs.copy()

    # -------------------- Unitless helpers --------------------

    def _get_flowrate(self) -> VolumetricFlowRate:
        if "flowrate" not in self.data:
            raise ValueError("flowrate is required (at least at the network/entry level).")
        return self.data["flowrate"]

    def _get_density(self) -> Density:
        if "density" in self.data:
            return self.data["density"]
        if "fluid" in self.data and isinstance(self.data["fluid"], Component):
            return self.data["fluid"].density()
        raise ValueError("Provide density or a fluid Component.")

    def _get_viscosity(self) -> Viscosity:
        if "viscosity" in self.data:
            return self.data["viscosity"]
        if "fluid" in self.data and isinstance(self.data["fluid"], Component):
            return self.data["fluid"].viscosity()   
        raise ValueError("Provide viscosity or a fluid Component.")

    # -------------------- Pipe-level calcs --------------------

    def _internal_diameter_m(self, pipe: Pipe) -> Diameter:
        if hasattr(pipe, "internal_diameter"):
            return pipe.internal_diameter  # mm → m
        return pipe.nominal_diameter  # assume already meters

    def _velocity(self, q_m3s: float, pipe: Pipe) -> Velocity:
        
        return FluidVelocity(volumetric_flow_rate=q_m3s, diameter=self._internal_diameter_m(pipe)).calculate()

    def _reynolds(self, v: float, pipe: Pipe) :
        return ReynoldsNumber(
                                density=self._get_density(),
                                velocity=v,
                                diameter=self._internal_diameter_m(pipe),
                                viscosity=self._get_viscosity(),
                                ).calculate()
        

    def _friction_factor(self, Re: float, pipe: Pipe) :
        return ColebrookWhite(
                                    reynolds_number=Re,
                                    roughness=float(pipe.roughness),
                                    diameter=self._internal_diameter_m(pipe),
                                ).calculate()
        

    def _major_loss_dp(self, f: float, v: float, pipe: Pipe) :
        return PressureDropDarcy(
            friction_factor=f,
            length=float(pipe.length),
            diameter=self._internal_diameter_m(pipe),
                density=self._get_density(),
                velocity=v,
            ).calculate()
        

    def _minor_loss_dp(self, K: float, v: float):
        rho = self._get_density()
        return float(K) * 0.5 * rho * (v**2)

    # -------------------- Series evaluation --------------------

    def _compute_series(self, elements: List[Any], q_m3s: float) -> Tuple[float, List[Dict[str, Any]]]:
        results = []
        dp_total = 0.0
        last_v = None

        for e in elements:
            if isinstance(e, Pipe):
                v = self._velocity(q_m3s, e)
                Re = self._reynolds(v, e)
                f = self._friction_factor(Re, e)
                dp = self._major_loss_dp(f, v, e)

                results.append({
                    "type": "pipe",
                    "name": getattr(e, "name", "pipe"),
                    "diameter_m": self._internal_diameter_m(e),
                    "velocity_m_s": v,
                    "reynolds_number": Re,
                    "friction_factor": f,
                    "pressure_drop_Pa": dp,
                })
                dp_total += dp
                last_v = v

            elif isinstance(e, Fitting):
                if last_v is None:
                    results.append({
                        "type": "fitting",
                        "name": getattr(e, "fitting_type", "fitting"),
                        "K": e.K,
                        "pressure_drop_Pa": None,
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
                dp_sub, sub_pipes, sub_branches = self._compute_network(e, q_m3s)
                results.extend(sub_pipes)
                dp_total += dp_sub

        return dp_total, results

    # -------------------- Parallel evaluation --------------------

    def _resolve_parallel_flows(self, net: PipelineNetwork, q_m3s: float, branches: List[Any]) -> List[float]:
        split_cfg = (self.data.get("flow_split") or {}).get(net.name)
        n = len(branches)

        if split_cfg is None:
            return [q_m3s / n] * n  # equal split

        vals = [float(x) for x in split_cfg]
        if sum(vals) > 1.5 * q_m3s:  # absolute flows
            return vals
        s = sum(vals)
        return [q_m3s * (v / s) for v in vals]

    def _compute_network(self, net: PipelineNetwork, q_m3s: float):
        if net.connection_type in (None, "series"):
            dp, pipes = self._compute_series(net.elements, q_m3s)
            return dp, pipes, []

        # Parallel block
        branches = net.elements
        q_branches = self._resolve_parallel_flows(net, q_m3s, branches)
        branch_summaries, all_pipe_results = [], []
        dp_across = 0.0

        for idx, (child, qb) in enumerate(zip(branches, q_branches), start=1):
            if isinstance(child, PipelineNetwork):
                dp_b, pipes_b, sub_branches = self._compute_network(child, qb)
                all_pipe_results.extend(pipes_b)
                branch_summaries.extend(sub_branches)
            else:
                dp_b, pipes_b = self._compute_series([child], qb)
                all_pipe_results.extend(pipes_b)

            branch_summaries.append({
                "parallel_name": net.name,
                "branch_index": idx,
                "flow_m3_s": qb,
                "pressure_drop_Pa": dp_b,
            })
            dp_across = max(dp_across, dp_b)

        return dp_across, all_pipe_results, branch_summaries

    # -------------------- Public API --------------------

    def run(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        # NETWORK MODE
        if "network" in self.data and isinstance(self.data["network"], PipelineNetwork):
            net = self.data["network"]
            q_in = self._get_flowrate()
            total_dp, pipe_results, branch_summaries = self._compute_network(net, q_in)

            results["mode"] = "network"
            results["summary"] = {"inlet_flow_m3_s": q_in, "total_pressure_drop_Pa": total_dp}
            results["pipes"] = pipe_results
            if branch_summaries:
                results["parallel_sections"] = branch_summaries
            if hasattr(net, "schematic"):
                results["schematic"] = net.schematic()
            return results

        # SINGLE PIPE MODE
        if "pipe" not in self.data:
            raise ValueError("Need a Pipe or a PipelineNetwork to run engine")

        pipe = self.data["pipe"]
        q = self._get_flowrate()

        v = self._velocity(q, pipe)
        Re = self._reynolds(v, pipe)
        f = self._friction_factor(Re, pipe)
        dp = self._major_loss_dp(f, v, pipe)

        results["mode"] = "single"
        results["pipe"] = {
            "diameter_m": self._internal_diameter_m(pipe),
            "length_m": float(pipe.length),
        }
        results["velocity_m_s"] = v
        results["reynolds_number"] = Re
        results["friction_factor"] = f
        results["pressure_drop_Pa"] = dp
        return results
