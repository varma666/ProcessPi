from typing import Dict, Any, Optional, List, Tuple, Union
from ..units import *
from .pipelineresults import PipelineResults
from ..components import Component
from ..calculations.fluids.optimium_pipe_dia import OptimumPipeDiameter
from ..pipelines.standards import get_nearest_diameter, get_recommended_velocity
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
    def __init__(self, **kwargs: Any):
        self.data: Dict[str, Any] = kwargs.copy()

    # -------------------- Helpers --------------------
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

    # -------------------- Pipe-level --------------------
    def _internal_diameter_m(self, pipe: Optional[Pipe] = None) -> Diameter:
        """
        Returns the internal diameter of a pipe. If not specified, calculates optimum diameter.
        """
        if pipe:
            if getattr(pipe, "internal_diameter", None) is not None:
                return pipe.internal_diameter
            if getattr(pipe, "nominal_diameter", None) is not None:
                return pipe.nominal_diameter

        # No pipe or no diameter → calculate optimum
        flowrate = self._get_flowrate()
        density = self._get_density()

        calc = OptimumPipeDiameter(flow_rate=flowrate, density=density)
        opt_diameter = calc.calculate()  # Already mapped to nearest standard
        return opt_diameter

    def _velocity(self, q_m3s: VolumetricFlowRate, pipe: Pipe) -> Velocity:
        """
        Computes fluid velocity. Adjusts pipe diameter to maintain recommended velocity if service type is known.
        """
        from math import sqrt, pi

        v_base = FluidVelocity(
            volumetric_flow_rate=q_m3s,
            diameter=self._internal_diameter_m(pipe)
        ).calculate()

        # Adjust for recommended velocity if fluid has service_type
        service = getattr(self.data.get("fluid"), "service_type", None)
        if service:
            rec = get_recommended_velocity(service)
            if rec:
                if isinstance(rec, tuple):
                    v_min, v_max = rec
                    if v_base < v_min or v_base > v_max:
                        target_v = sum(rec)/2
                        A_new = q_m3s.value / target_v
                        D_new = sqrt(4*A_new/pi)
                        pipe.internal_diameter = Diameter(D_new*1000, "mm")
                        v_base = target_v
                else:  # single value
                    if abs(v_base - rec)/rec > 0.1:
                        target_v = rec
                        A_new = q_m3s.value / target_v
                        D_new = sqrt(4*A_new/pi)
                        pipe.internal_diameter = Diameter(D_new*1000, "mm")
                        v_base = target_v

        return v_base

    def _reynolds(self, v: float, pipe: Pipe):
        return ReynoldsNumber(
            density=self._get_density(),
            velocity=v,
            diameter=self._internal_diameter_m(pipe),
            viscosity=self._get_viscosity(),
        ).calculate()

    def _friction_factor(self, Re: float, pipe: Pipe):
        return ColebrookWhite(
            reynolds_number=Re,
            roughness=float(pipe.roughness),
            diameter=self._internal_diameter_m(pipe),
        ).calculate()

    def _major_loss_dp(self, f: float, v: float, pipe: Pipe):
        return PressureDropDarcy(
            friction_factor=f,
            length=pipe.length,
            diameter=self._internal_diameter_m(pipe),
            density=self._get_density(),
            velocity=v,
        ).calculate()

    def _minor_loss_dp(self, fitting: Fitting, v: Velocity, f: Optional[float] = None, d: Optional[Diameter] = None):
        """Compute minor loss for a fitting."""
        rho = self._get_density()
        # Extract numeric values
        v_val = v.value if hasattr(v, "value") else v
        d_val = d.value if hasattr(d, "value") else d
        f_val = f.value if hasattr(f, "value") else f

        if getattr(fitting, "K", None) is not None:
            return Pressure(float(fitting.K) * 0.5 * (rho.value if hasattr(rho, "value") else rho) * (v_val**2), "Pa")
        elif getattr(fitting, "Le", None) is not None:
            if f_val is None or d_val is None:
                raise ValueError("Friction factor and diameter are required for equivalent length method.")
            return Pressure(f_val * (fitting.Le / d_val) * 0.5 * (rho.value if hasattr(rho, "value") else rho) * (v_val**2), "Pa")
        else:
            return Pressure(0.0, "Pa")


    # -------------------- Series evaluation --------------------
    def _compute_series(self, series_list, flow_rate, fluid):
        """
        Compute pressure drop and flow parameters for a series of pipeline elements.
        Supports: Pipes, Pumps, Equipment, and Vessels.
        """
        results = []
        dp_total = Pressure(0, "Pa")
    
        for element in series_list:
            # --- Handle Pipe ---
            if isinstance(element, Pipe):
                pipe_result = self.pipe_calculation(element, flow_rate, fluid)
                dp_total += pipe_result["pressure_drop"]
                results.append({
                    "type": "pipe",
                    "name": getattr(element, "name", "pipe"),
                    "length": element.length,
                    "diameter": element.diameter,
                    "pressure_drop_Pa": pipe_result["pressure_drop"],
                    "reynolds": pipe_result["reynolds"],
                    "friction_factor": pipe_result["friction_factor"]
                })
    
            # --- Handle Pump (Head Gain) ---
            elif isinstance(element, Pump):
                pump_gain = element.head_gain.to("Pa")  # convert pump head gain to Pa
                dp_total -= pump_gain  # subtracting pump gain from total system loss
                results.append({
                    "type": "pump",
                    "name": getattr(element, "name", "pump"),
                    "head_gain_Pa": pump_gain
                })
    
            # --- Handle Equipment (Pressure Drop) ---
            elif isinstance(element, Equipment):
                eq_dp = element.pressure_drop.to("Pa") if element.pressure_drop else Pressure(0, "Pa")
                dp_total += eq_dp
                results.append({
                    "type": "equipment",
                    "name": getattr(element, "name", "equipment"),
                    "pressure_drop_Pa": eq_dp
                })
    
            # --- Handle Vessel (Static Head or Minimal Drop) ---
            elif isinstance(element, Vessel):
                vessel_dp = element.pressure_drop.to("Pa") if element.pressure_drop else Pressure(0, "Pa")
                dp_total += vessel_dp
                results.append({
                    "type": "vessel",
                    "name": getattr(element, "name", "vessel"),
                    "pressure_drop_Pa": vessel_dp
                })
    
            # --- Unknown Component ---
            else:
                raise TypeError(f"Unsupported element type: {type(element).__name__}")
    
        return {
            "type": "series",
            "pressure_drop_total_Pa": dp_total,
            "elements": results
        }


    # -------------------- Parallel evaluation --------------------
    def _resolve_parallel_flows(self, net: PipelineNetwork, q_m3s: VolumetricFlowRate, branches: List[Any]) -> List[float]:
        split_cfg = (self.data.get("flow_split") or {}).get(net.name)
        n = len(branches)
        if split_cfg is None:
            return [q_m3s.value / n] * n  # equal split
        vals = [float(x) for x in split_cfg]
        if sum(vals) > 1.5 * q_m3s.value:  # absolute flows
            return vals
        s = sum(vals)
        return [q_m3s.value * (v / s) for v in vals]

    def _compute_network(self, net: PipelineNetwork, q_m3s: VolumetricFlowRate):
        if net.connection_type in (None, "series"):
            dp, pipes = self._compute_series(net.elements, q_m3s)
            return dp, pipes, []

        # Parallel block
        branches = net.elements
        q_branches = self._resolve_parallel_flows(net, q_m3s, branches)
        branch_summaries, all_pipe_results = [], []
        dp_across = Pressure(0.0, "Pa")
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

    # -------------------- RUN --------------------
    def run(self) -> "PipelineResults":
        results: Dict[str, Any] = {}

        # Get flowrate
        q_in = self._get_flowrate()

        # -------------------- PIPE / OPTIMUM PIPE HANDLING --------------------
        if "pipe" in self.data:
            pipe = self.data["pipe"]
        elif "network" not in self.data:
            # No pipe or network provided, create optimum pipe
            opt_diameter = OptimumPipeDiameter(
                flow_rate=q_in,
                density=self._get_density()
            ).calculate()  # Diameter object, already nearest standard

            pipe = Pipe(
                nominal_diameter=opt_diameter,
                schedule="40",               # default schedule
                material="CS",               # default material
                length=Length(1.0, "m")      # default length 1 m
            )
            self.data["pipe"] = pipe

        # -------------------- NETWORK MODE --------------------
        if "network" in self.data and isinstance(self.data["network"], PipelineNetwork):
            net = self.data["network"]
            total_dp, pipe_results, branch_summaries = self._compute_network(net, q_in)

            results["mode"] = "network"
            results["summary"] = {"inlet_flow_m3_s": q_in.value, "total_pressure_drop_Pa": total_dp.value}
            results["pipes"] = pipe_results
            if branch_summaries:
                results["parallel_sections"] = branch_summaries
            if hasattr(net, "schematic"):
                results["schematic"] = net.schematic()

        # -------------------- SINGLE PIPE MODE --------------------
        else:
            v = self._velocity(q_in, pipe)
            Re = self._reynolds(v, pipe)
            f = self._friction_factor(Re, pipe)
            dp = self._major_loss_dp(f, v, pipe)

            results["mode"] = "single"
            results["pipe"] = {
                "internal_diameter": pipe.internal_diameter,
                "length": pipe.length,
            }
            results["velocity_m_s"] = v
            results["reynolds_number"] = Re
            results["friction_factor"] = f
            results["pressure_drop_Pa"] = dp

        # Store results internally for summary
        self._results = results

        # Return wrapper object
        return PipelineResults(results)


    # processpi/pipelines/engine.py

    def summary(self):
        """Print a clean, human-readable summary of the last run."""
        if not hasattr(self, "_results") or not self._results:
            raise ValueError("No results found. Run the engine first with engine.run()")

        results = self._results
        print("\n=== Pipeline Summary ===")

        # -------------------- Network summary --------------------
        summary = results.get("summary", {})
        if summary:
            inlet_flow = summary.get("inlet_flow_m3_s")
            total_dp = summary.get("total_pressure_drop_Pa")
            if inlet_flow:
                fval = inlet_flow.value if hasattr(inlet_flow, "value") else inlet_flow
                print(f"Inlet Flow: {fval:.3f} m³/s")
            if total_dp:
                fval = total_dp.value if hasattr(total_dp, "value") else total_dp
                print(f"Total Pressure Drop: {fval:.2f} Pa")

        # -------------------- Single Pipe Mode --------------------
        if results.get("mode") == "single":
            pipe_data = results.get("pipe", {})
            d = pipe_data.get("internal_diameter")
            l = pipe_data.get("length")
            v = results.get("velocity_m_s")
            Re = results.get("reynolds_number")
            f = results.get("friction_factor")
            dp = results.get("pressure_drop_Pa")

            print("\n--- Single Pipe ---")
            if d:
                print(f"Pipe Internal Diameter: {d.value:.2f} mm")
            if l:
                print(f"Pipe Length: {l.value:.2f} m")
            if v:
                print(f"Velocity: {v.value:.3f} m/s")
            if Re is not None:
                re_val = Re.value if hasattr(Re, "value") else Re
                print(f"Reynolds Number: {re_val:.0f}")
            if f is not None:
                fval = f.value if hasattr(f, "value") else f
                print(f"Friction Factor: {fval:.4f}")
            if dp:
                print(f"Pressure Drop: {dp.value:.2f} Pa")

        # -------------------- Network / Multiple Pipes --------------------
        pipes = results.get("pipes", [])
        if pipes:
            print("\n--- Pipe & Fitting Details ---")
            for p in pipes:
                if p["type"] == "pipe":
                    d = p.get("diameter_m")
                    v = p.get("velocity_m_s")
                    Re = p.get("reynolds_number")
                    f = p.get("friction_factor")
                    dp = p.get("pressure_drop_Pa")
                    print(f"\nPipe: {p.get('name','pipe')}")
                    if d:
                        d_val = d.value if hasattr(d, "value") else d
                        print(f"  Diameter: {d_val:.2f} mm")
                    if v:
                        v_val = v.value if hasattr(v, "value") else v
                        print(f"  Velocity: {v_val:.3f} m/s")
                    if Re is not None:
                        re_val = Re.value if hasattr(Re, "value") else Re
                        print(f"  Reynolds #: {re_val:.0f}")
                    if f is not None:
                        f_val = f.value if hasattr(f, "value") else f
                        print(f"  Friction Factor: {f_val:.4f}")
                    if dp:
                        dp_val = dp.value if hasattr(dp, "value") else dp
                        print(f"  Pressure Drop: {dp_val:.2f} Pa")
                elif p["type"] == "fitting":
                    dp = p.get("pressure_drop_Pa")
                    print(f"\nFitting: {p.get('name','fitting')}")
                    print(f"  K-factor: {p.get('K')}")
                    if dp:
                        dp_val = dp.value if hasattr(dp, "value") else dp
                        print(f"  Pressure Drop: {dp_val:.2f} Pa")

        # -------------------- Schematic --------------------
        if "schematic" in results:
            print("\n=== Schematic ===")
            print(results["schematic"])
