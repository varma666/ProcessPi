from typing import Dict, Any, Optional, List, Tuple, Union
from ..units import *
from .pipelineresults import PipelineResults
from ..components import Component
from ..calculations.fluids.optimium_pipe_dia import OptimumPipeDiameter
from ..pipelines.standards import get_recommended_velocity
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
    Flexible engine:
      - Accepts flowrate OR velocity (and derives the other when diameter/pipe exists)
      - Can run single-pipe or network mode
      - Preserves original core logic

    Accepted input aliases in kwargs (all optional; provide what you have):
      flowrate | flow_rate | q
      velocity | v
      pipe
      diameter | dia | nominal_diameter | internal_diameter
      length | len
      fluid
      density
      viscosity
      network
      flow_split (for parallel branches)
    """
    # -------------------- INIT --------------------
    def __init__(self, **kwargs: Any):
        # Keep original storage so existing code using self.data[...] still works
        self.data: Dict[str, Any] = kwargs.copy()

        # Normalize common aliases into self.data without removing originals
        alias_map = {
            "flowrate": ["flow_rate", "q"],
            "velocity": ["v"],
            "diameter": ["dia", "nominal_diameter", "internal_diameter"],
            "length": ["len"],
        }
        for canon, alts in alias_map.items():
            if canon not in self.data:
                for alt in alts:
                    if alt in self.data:
                        self.data[canon] = self.data[alt]
                        break

    # -------------------- Helpers --------------------
    def _get_density(self) -> Density:
        if "density" in self.data and self.data["density"] is not None:
            return self.data["density"]
        if "fluid" in self.data and isinstance(self.data["fluid"], Component):
            return self.data["fluid"].density()
        raise ValueError("Provide density or a fluid Component (with .density()).")

    def _get_viscosity(self) -> Viscosity:
        if "viscosity" in self.data and self.data["viscosity"] is not None:
            return self.data["viscosity"]
        if "fluid" in self.data and isinstance(self.data["fluid"], Component):
            return self.data["fluid"].viscosity()
        raise ValueError("Provide viscosity or a fluid Component (with .viscosity()).")

    def _ensure_pipe(self) -> Pipe:
        """
        Return a Pipe instance from:
          - self.data['pipe'] if present
          - otherwise create a minimal Pipe if diameter/length are provided
          - otherwise (single-pipe mode only) create an optimum-diameter pipe if we can compute flowrate
        """
        # If a Pipe is already provided, use it
        if "pipe" in self.data and isinstance(self.data["pipe"], Pipe):
            return self.data["pipe"]

        # If caller provided a raw diameter/length, create a Pipe shell
        dia = self.data.get("diameter")
        length = self.data.get("length") or Length(1.0, "m")

        if dia is not None:
            # Accept Diameter directly, or try to wrap Number (assumed mm)
            if not isinstance(dia, Diameter):
                # fallback assumption: millimeters
                dia = Diameter(float(dia), "mm")
            # Build a pipe with given internal diameter
            p = Pipe(internal_diameter=dia, length=length)
            self.data["pipe"] = p
            return p

        # As a last resort for single-pipe mode (no network), compute optimum diameter
        # if we can determine a flowrate (either directly or from velocity & some diameter-like info)
        if "network" not in self.data:
            q = self._maybe_flowrate()  # may raise if insufficient inputs
            calc = OptimumPipeDiameter(flow_rate=q, density=self._get_density())
            opt_diameter = calc.calculate()
            p = Pipe(nominal_diameter=opt_diameter, length=length)
            self.data["pipe"] = p
            return p

        # If in network mode, element pipes should come from the network elements
        raise ValueError("No pipe or diameter provided. In network mode, provide pipes in the network elements.")

    def _internal_diameter_m(self, pipe: Optional[Pipe] = None) -> Diameter:
        """
        Returns the internal diameter. If not set on the pipe, uses nominal_diameter.
        Single-pipe mode may compute optimum diameter (handled by _ensure_pipe()).
        """
        if pipe:
            if getattr(pipe, "internal_diameter", None) is not None:
                return pipe.internal_diameter
            if getattr(pipe, "nominal_diameter", None) is not None:
                return pipe.nominal_diameter

        # Fallback to engine-level diameter (if provided)
        if "diameter" in self.data and self.data["diameter"] is not None:
            d = self.data["diameter"]
            return d if isinstance(d, Diameter) else Diameter(float(d), "mm")

        # As a final fallback (single-pipe) compute optimum using flowrate
        q = self._maybe_flowrate()  # may raise
        calc = OptimumPipeDiameter(flow_rate=q, density=self._get_density())
        return calc.calculate()

    def _maybe_flowrate(self) -> VolumetricFlowRate:
        """
        Return a VolumetricFlowRate if it can be determined from inputs.
        Priority:
          1) Explicit 'flowrate'
          2) velocity + diameter (from engine or pipe)
        Else: raise ValueError.
        """
        # 1) Direct
        if "flowrate" in self.data and self.data["flowrate"] is not None:
            return self.data["flowrate"]

        # 2) Compute from velocity & diameter (engine-level or pipe)
        vel = self.data.get("velocity")
        if vel is not None:
            # Ensure we have a diameter either at engine-level or in a pipe
            d = self.data.get("diameter")
            pipe = self.data.get("pipe") if isinstance(self.data.get("pipe"), Pipe) else None
            if d is None and pipe is not None:
                d = self._internal_diameter_m(pipe)
            if d is None:
                raise ValueError("To derive flowrate from velocity, provide a diameter or a Pipe with diameter.")
            if not isinstance(d, Diameter):
                d = Diameter(float(d), "mm")
            q = FluidVelocity(volumetric_flow_rate=None, diameter=d, velocity=vel).invert_to_flowrate()
            # Some FluidVelocity implementations return a VolumetricFlowRate via .calculate(), here we define helper:
            if isinstance(q, VolumetricFlowRate):
                self.data["flowrate"] = q
                return q
            # If invert_to_flowrate not available, compute via area
            from math import pi
            v_val = vel.value if hasattr(vel, "value") else float(vel)
            d_m = d.to("m").value if hasattr(d, "to") else d.value
            area = pi * (d_m ** 2) / 4.0
            q_m3s = v_val * area
            q = VolumetricFlowRate(q_m3s, "m^3/s")
            self.data["flowrate"] = q
            return q

        raise ValueError(
            "Unable to determine flowrate. Provide 'flowrate' or 'velocity' plus a 'diameter' (or a Pipe with diameter)."
        )

    def _maybe_velocity(self, pipe: Pipe) -> Velocity:
        """
        Return Velocity if available or derivable:
          1) Explicit 'velocity'
          2) From flowrate & diameter
        Also adjusts diameter to recommended velocity range if service_type is present.
        """
        # 1) Direct
        if "velocity" in self.data and self.data["velocity"] is not None:
            v = self.data["velocity"]
            # Optional: adjust pipe diameter to recommended velocity if service exists
            self._apply_recommended_velocity(pipe, given_velocity=v)
            return v

        # 2) From flowrate & diameter
        q = self._maybe_flowrate()
        v = FluidVelocity(volumetric_flow_rate=q, diameter=self._internal_diameter_m(pipe)).calculate()
        # Adjust pipe diameter if service_type recommendation exists
        self._apply_recommended_velocity(pipe, flowrate=q, computed_velocity=v)
        return v

    def _apply_recommended_velocity(
        self,
        pipe: Pipe,
        flowrate: Optional[VolumetricFlowRate] = None,
        computed_velocity: Optional[Velocity] = None,
        given_velocity: Optional[Velocity] = None,
    ) -> None:
        """
        If fluid has a service_type with recommended velocity range, optionally adjust pipe diameter
        to target midpoint velocity (non-destructive to results beyond updating pipe.internal_diameter).
        """
        service = getattr(self.data.get("fluid"), "service_type", None)
        if not service:
            return

        rec = get_recommended_velocity(service)
        if not rec:
            return

        # Current velocity
        v_curr = given_velocity or computed_velocity
        if v_curr is None and flowrate is not None:
            v_curr = FluidVelocity(volumetric_flow_rate=flowrate, diameter=self._internal_diameter_m(pipe)).calculate()
        if v_curr is None:
            return

        # Convert tuple / single
        if isinstance(rec, tuple):
            v_min, v_max = rec
            # Only adjust if out of range by >10%
            if v_curr < v_min or v_curr > v_max:
                target_v = (v_min + v_max) / 2.0
            else:
                return
        else:
            # Single recommended value; adjust if off by >10%
            target_v = rec
            v_val = v_curr.value if hasattr(v_curr, "value") else float(v_curr)
            if abs(v_val - target_v) / target_v <= 0.1:
                return

        # Need flowrate to adjust diameter
        q = flowrate or self._maybe_flowrate()
        from math import sqrt, pi
        A_new = q.value / target_v
        D_new = sqrt(4.0 * A_new / pi)
        pipe.internal_diameter = Diameter(D_new * 1000.0, "mm")  # set in mm

    # -------------------- Core calcs --------------------
    def _reynolds(self, v: Velocity, pipe: Pipe):
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

    def _major_loss_dp(self, f: float, v: Velocity, pipe: Pipe):
        return PressureDropDarcy(
            friction_factor=f,
            length=pipe.length,
            diameter=self._internal_diameter_m(pipe),
            density=self._get_density(),
            velocity=v,
        ).calculate()

    def _minor_loss_dp(
        self,
        fitting: Fitting,
        v: Velocity,
        f: Optional[float] = None,
        d: Optional[Diameter] = None
    ) -> Pressure:
        """Compute minor loss for a fitting (K or equivalent length)."""
        rho = self._get_density()
        v_val = v.value if hasattr(v, "value") else float(v)
        d_val = d.value if hasattr(d, "value") else (d if d is not None else None)
        f_val = f.value if hasattr(f, "value") else (f if f is not None else None)

        rho_val = rho.value if hasattr(rho, "value") else float(rho)

        if getattr(fitting, "K", None) is not None:
            return Pressure(float(fitting.K) * 0.5 * rho_val * (v_val ** 2), "Pa")
        elif getattr(fitting, "Le", None) is not None:
            if f_val is None or d_val is None:
                raise ValueError("Friction factor and diameter are required for equivalent length method.")
            return Pressure(f_val * (fitting.Le / d_val) * 0.5 * rho_val * (v_val ** 2), "Pa")
        else:
            return Pressure(0.0, "Pa")

    # -------------------- Series evaluation --------------------
    def _pipe_calculation(self, pipe: Pipe, flow_rate: Optional[VolumetricFlowRate]) -> Dict[str, Any]:
        """
        Internal helper used by _compute_series: compute v, Re, f, dp for a given pipe.
        """
        # Prefer provided flow_rate, else try engine-level (maybe derived from velocity)
        q = flow_rate or (self.data.get("flowrate") if self.data.get("flowrate") else None)
        if q is None and self.data.get("velocity"):
            # Derive a flow from velocity if necessary for recommended velocity adjustment, but we can also
            # compute dp directly with given velocity.
            pass

        # Velocity: given or computed from q & pipe diameter
        if self.data.get("velocity") is not None:
            v = self.data["velocity"]
        else:
            if q is None:
                # If nothing available, compute v from pipe & any engine-level flowrate if possible
                q = self._maybe_flowrate()
            v = FluidVelocity(volumetric_flow_rate=q, diameter=self._internal_diameter_m(pipe)).calculate()

        # Reynolds / Friction / Major losses
        Re = self._reynolds(v, pipe)
        f = self._friction_factor(Re, pipe)
        dp = self._major_loss_dp(f, v, pipe)

        return {
            "velocity": v,
            "reynolds": Re,
            "friction_factor": f,
            "pressure_drop": dp,
        }

    def _compute_series(self, series_list: List[Any], flow_rate: Optional[VolumetricFlowRate], fluid: Optional[Component]):
        """
        Compute pressure drop and flow parameters for a series of pipeline elements.
        Supports: Pipes, Pumps (head_gain), and generic Equipment/Vessels (pressure_drop).
        Also considers inlet and outlet pressures if defined for any element (adds to dp_total).
        """
        results = []
        dp_total = Pressure(0, "Pa")

        for element in series_list:
            element_name = getattr(element, "name", element.__class__.__name__.lower())

            # --- Pipe ---
            if isinstance(element, Pipe):
                calc = self._pipe_calculation(element, flow_rate)
                dp_total += calc["pressure_drop"]

                results.append({
                    "type": "pipe",
                    "name": element_name,
                    "length": element.length,
                    "diameter": self._internal_diameter_m(element),
                    "pressure_drop_Pa": calc["pressure_drop"],
                    "reynolds": calc["reynolds"],
                    "friction_factor": calc["friction_factor"],
                    "velocity": calc["velocity"],
                })

            # --- Pump-like (duck typing: has head_gain) ---
            elif hasattr(element, "head_gain") and element.head_gain is not None:
                pump_gain = element.head_gain.to("Pa")
                dp_total -= pump_gain  # pump adds energy
                results.append({
                    "type": "pump",
                    "name": element_name,
                    "head_gain_Pa": pump_gain
                })

            # --- Equipment/Vessel-like (duck typing: has pressure_drop) ---
            elif hasattr(element, "pressure_drop"):
                eq_dp = element.pressure_drop.to("Pa") if element.pressure_drop else Pressure(0, "Pa")
                dp_total += eq_dp
                results.append({
                    "type": getattr(element, "equipment_type", "equipment"),
                    "name": element_name,
                    "pressure_drop_Pa": eq_dp
                })

            else:
                raise TypeError(f"Unsupported element type: {type(element).__name__}")

            # --- Optional inlet/outlet pressures on any element ---
            inlet_p = getattr(element, "inlet_pressure", None)
            outlet_p = getattr(element, "outlet_pressure", None)
            if inlet_p is not None and outlet_p is not None:
                dp_element = inlet_p.to("Pa") - outlet_p.to("Pa")
                dp_total += dp_element
                results[-1].update({
                    "inlet_pressure_Pa": inlet_p.to("Pa"),
                    "outlet_pressure_Pa": outlet_p.to("Pa"),
                    "net_dp_from_defined_pressures_Pa": dp_element
                })

        return dp_total, results

    # -------------------- Parallel evaluation --------------------
    def _resolve_parallel_flows(self, net: PipelineNetwork, q_m3s: VolumetricFlowRate, branches: List[Any]) -> List[float]:
        split_cfg = (self.data.get("flow_split") or {}).get(net.name) if isinstance(self.data.get("flow_split"), dict) else None
        n = len(branches)
        if split_cfg is None:
            return [q_m3s.value / n] * n  # equal split
        vals = [float(x) for x in split_cfg]
        if sum(vals) > 1.5 * q_m3s.value:  # treat as absolute flows
            return vals
        s = sum(vals)
        return [q_m3s.value * (v / s) for v in vals]

    def _compute_network(self, net: PipelineNetwork, q_m3s: VolumetricFlowRate):
        """
        Recursively compute pressure drops across a network with series/parallel blocks.
        Returns: (dp_across, pipe_results, branch_summaries)
        """
        if net.connection_type in (None, "series"):
            dp_total, elems = self._compute_series(net.elements, q_m3s, self.data.get("fluid"))
            return dp_total, elems, []

        # Parallel block
        branches = net.elements
        q_branches = self._resolve_parallel_flows(net, q_m3s, branches)
        branch_summaries, all_results = [], []
        dp_across = Pressure(0.0, "Pa")

        for idx, (child, qb) in enumerate(zip(branches, q_branches), start=1):
            if isinstance(child, PipelineNetwork):
                dp_b, pipes_b, sub_branches = self._compute_network(child, VolumetricFlowRate(qb, "m^3/s"))
                all_results.extend(pipes_b)
                branch_summaries.extend(sub_branches)
            else:
                dp_b, pipes_b = self._compute_series([child], VolumetricFlowRate(qb, "m^3/s"), self.data.get("fluid"))
                all_results.extend(pipes_b)
                branch_summaries.append({
                    "parallel_name": net.name,
                    "branch_index": idx,
                    "flow_m3_s": qb,
                    "pressure_drop_Pa": dp_b,
                })
            # Parallel sets equalize to the highest branch drop
            dp_across = max(dp_across, dp_b)

        return dp_across, all_results, branch_summaries

    # -------------------- RUN --------------------
    def run(self) -> "PipelineResults":
        results: Dict[str, Any] = {}

        # Network mode?
        if "network" in self.data and isinstance(self.data["network"], PipelineNetwork):
            q_in = self._maybe_flowrate()  # inlet flow must be determinable
            net = self.data["network"]
            total_dp, pipe_results, branch_summaries = self._compute_network(net, q_in)

            results["mode"] = "network"
            results["summary"] = {
                "inlet_flow_m3_s": q_in,
                "total_pressure_drop_Pa": total_dp
            }
            results["pipes"] = pipe_results
            if branch_summaries:
                results["parallel_sections"] = branch_summaries
            if hasattr(net, "schematic"):
                results["schematic"] = net.schematic()

        # Single-pipe mode
        else:
            pipe = self._ensure_pipe()
            v = self._maybe_velocity(pipe)          # velocity (given or computed)
            Re = self._reynolds(v, pipe)
            f = self._friction_factor(Re, pipe)
            dp = self._major_loss_dp(f, v, pipe)

            results["mode"] = "single"
            results["pipe"] = {
                "internal_diameter": self._internal_diameter_m(pipe),
                "length": pipe.length,
            }
            results["velocity_m_s"] = v
            results["reynolds_number"] = Re
            results["friction_factor"] = f
            results["pressure_drop_Pa"] = dp

        # Store results internally for summary()
        self._results = results
        return PipelineResults(results)

    # -------------------- Summary --------------------
    def summary(self):
        """Print a clean, human-readable summary of the last run."""
        if not hasattr(self, "_results") or not self._results:
            raise ValueError("No results found. Run the engine first with engine.run()")

        results = self._results
        print("\n=== Pipeline Summary ===")

        # Network summary
        summary = results.get("summary", {})
        if summary:
            inlet_flow = summary.get("inlet_flow_m3_s")
            total_dp = summary.get("total_pressure_drop_Pa")
            if inlet_flow:
                fval = inlet_flow.value if hasattr(inlet_flow, "value") else inlet_flow
                print(f"Inlet Flow: {fval:.6f} m³/s")
            if total_dp:
                fval = total_dp.value if hasattr(total_dp, "value") else total_dp
                print(f"Total Pressure Drop: {fval:.2f} Pa")

        # Single-pipe section
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
                d_val = d.value if hasattr(d, "value") else d
                print(f"Pipe Internal Diameter: {d_val:.2f} mm")
            if l:
                l_val = l.value if hasattr(l, "value") else l
                print(f"Pipe Length: {l_val:.2f} m")
            if v:
                v_val = v.value if hasattr(v, "value") else v
                print(f"Velocity: {v_val:.6f} m/s")
            if Re is not None:
                re_val = Re.value if hasattr(Re, "value") else Re
                print(f"Reynolds Number: {re_val:.0f}")
            if f is not None:
                fval = f.value if hasattr(f, "value") else f
                print(f"Friction Factor: {fval:.6f}")
            if dp:
                dp_val = dp.value if hasattr(dp, "value") else dp
                print(f"Pressure Drop: {dp_val:.2f} Pa")

        # Multi-element / Network details
        pipes = results.get("pipes", [])
        if pipes:
            print("\n--- Element Details ---")
            for p in pipes:
                t = p.get("type", "element")
                print(f"\n{t.capitalize()}: {p.get('name','element')}")
                if t == "pipe":
                    d = p.get("diameter")
                    v = p.get("velocity")
                    Re = p.get("reynolds")
                    f = p.get("friction_factor")
                    dp = p.get("pressure_drop_Pa")
                    if d:
                        d_val = d.value if hasattr(d, "value") else d
                        print(f"  Diameter: {d_val:.2f} mm")
                    if v:
                        v_val = v.value if hasattr(v, "value") else v
                        print(f"  Velocity: {v_val:.6f} m/s")
                    if Re is not None:
                        re_val = Re.value if hasattr(Re, "value") else Re
                        print(f"  Reynolds #: {re_val:.0f}")
                    if f is not None:
                        f_val = f.value if hasattr(f, "value") else f
                        print(f"  Friction Factor: {f_val:.6f}")
                    if dp:
                        dp_val = dp.value if hasattr(dp, "value") else dp
                        print(f"  Pressure Drop: {dp_val:.2f} Pa")
                elif t == "pump":
                    gain = p.get("head_gain_Pa")
                    if gain:
                        g_val = gain.value if hasattr(gain, "value") else gain
                        print(f"  Head Gain: {g_val:.2f} Pa")
                else:
                    dp = p.get("pressure_drop_Pa")
                    if dp:
                        dp_val = dp.value if hasattr(dp, "value") else dp
                        print(f"  Pressure Drop: {dp_val:.2f} Pa")

        if "schematic" in results:
            print("\n=== Schematic ===")
            print(results["schematic"])
