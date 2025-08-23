# processpi/pipelines/engine.py

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union

# Package-local imports expected in your project. Adjust if your paths differ.
from ..units import (
    Diameter, Length, Pressure, Density, Viscosity, VolumetricFlowRate, Velocity
)
from .pipelineresults import PipelineResults  # wrapper/DTO (assumed to exist in your project)
from ..components import Component            # fluids with .density() / .viscosity() / optional .service_type
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
    Sklearn-like interface:

        engine = PipelineEngine()
        engine.fit(
            flowrate=VolumetricFlowRate(...),         # or mass_flowrate + density
            mass_flowrate=..., density=..., viscosity=...,
            velocity=Velocity(...),                   # optional (if missing, computed)
            pipe=Pipe(...),                           # optional
            diameter=Diameter(...) or number(mm),     # optional
            length=Length(...),                       # optional if pipe provided
            fluid=Component(...),                     # optional if density & viscosity given
            network=PipelineNetwork(...),             # optional (else single-pipe mode)
            flow_split={"Parallel-AB": [0.3, 0.7]},   # optional branch allocation
            fittings=[Fitting(...), ...],             # optional minor losses in single-pipe mode
            inlet_pressure=Pressure(...),             # optional
            outlet_pressure=Pressure(...),            # optional
            available_dp=Pressure(...),               # optional: if given & diameter missing, engine can size pipe
            target_outlet_pressure=Pressure(...),     # optional: compute residual dp for control valve
        ).run()

    - If diameter is missing (single-pipe), engine uses OptimumPipeDiameter based on flowrate & density.
    - If flowrate missing, engine infers it from (mass_flowrate, density) or (velocity, diameter).
    - Supports series/parallel PipelineNetwork with configurable flow splits.
    - Computes residual DP (e.g., for CV) if inlet/outlet/available_dp are provided.
    """

    # -------------------- INIT / FIT --------------------
    def __init__(self, **kwargs: Any) -> None:
        self.data: Dict[str, Any] = {}
        if kwargs:
            self.fit(**kwargs)

    def fit(self, **kwargs: Any) -> "PipelineEngine":
        """
        Accepts optional inputs; normalizes common aliases; stores raw config for run().
        Returns self (sklearn-style).
        """
        # Shallow copy to preserve caller values
        self.data = dict(kwargs)

        # Normalize aliases without discarding originals
        alias_map = {
            "flowrate": ["flow_rate", "q", "Q"],
            "mass_flowrate": ["mass_flow", "m_dot", "mdot"],
            "velocity": ["v"],
            "diameter": ["dia", "D", "nominal_diameter", "internal_diameter"],
            "length": ["len", "L"],
            "inlet_pressure": ["in_pressure", "pin", "p_in"],
            "outlet_pressure": ["out_pressure", "pout", "p_out"],
            "available_dp": ["available_pressure_drop", "dp_available"],
            "target_outlet_pressure": ["target_pout"],
        }
        for canon, alts in alias_map.items():
            if canon not in self.data:
                for alt in alts:
                    if alt in self.data and self.data[alt] is not None:
                        self.data[canon] = self.data[alt]
                        break

        # Basic defaults (non-destructive)
        self.data.setdefault("flow_split", {})       # for parallel branches
        self.data.setdefault("fittings", [])         # minor-loss list in single-pipe mode
        self.data.setdefault("assume_mm_for_numbers", True)  # numeric diameter assumed mm

        # Light validation
        network = self.data.get("network")
        if network is not None and not isinstance(network, PipelineNetwork):
            raise TypeError("network must be a PipelineNetwork if provided.")

        return self

    # -------------------- Internal getters / inference ------------------------

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

    def _infer_flowrate(self) -> VolumetricFlowRate:
        """
        Infer volumetric flowrate from:
          1) explicit flowrate
          2) mass_flowrate & density
          3) velocity & diameter
        """
        # 1) Direct
        q = self.data.get("flowrate")
        if q is not None:
            return q

        # 2) From mass flow & density
        m = self.data.get("mass_flowrate")
        if m is not None:
            rho = self._get_density()
            # Volumetric flow = mass flow / density
            q = VolumetricFlowRate((m.value if hasattr(m, "value") else float(m)) /
                                   (rho.value if hasattr(rho, "value") else float(rho)), "m^3/s")
            self.data["flowrate"] = q
            return q

        # 3) From velocity & diameter
        vel = self.data.get("velocity")
        d = self.data.get("diameter")
        if vel is not None and (d is not None or isinstance(self.data.get("pipe"), Pipe)):
            if d is None:
                d = self._internal_diameter_m(self.data.get("pipe"))
            if not isinstance(d, Diameter):
                if self.data.get("assume_mm_for_numbers", True):
                    d = Diameter(float(d), "mm")
                else:
                    d = Diameter(float(d), "m")
            q = FluidVelocity(volumetric_flow_rate=None, diameter=d, velocity=vel).invert_to_flowrate()
            if not isinstance(q, VolumetricFlowRate):
                # fallback via area
                from math import pi
                v_val = vel.value if hasattr(vel, "value") else float(vel)
                d_m = d.to("m").value
                q = VolumetricFlowRate(v_val * (pi * d_m * d_m / 4.0), "m^3/s")
            self.data["flowrate"] = q
            return q

        raise ValueError("Unable to infer flowrate. Provide flowrate, or (mass_flowrate & density), or (velocity & diameter).")

    def _ensure_pipe(self) -> Pipe:
        """Return a Pipe or construct one (single-pipe mode) if possible."""
        p = self.data.get("pipe")
        if isinstance(p, Pipe):
            return p

        # Build from diameter/length if provided
        d = self.data.get("diameter")
        L = self.data.get("length") or Length(1.0, "m")
        if d is not None:
            if not isinstance(d, Diameter):
                if self.data.get("assume_mm_for_numbers", True):
                    d = Diameter(float(d), "mm")
                else:
                    d = Diameter(float(d), "m")
            p = Pipe(internal_diameter=d, length=L)
            self.data["pipe"] = p
            return p

        # Else compute optimum diameter (single-pipe only)
        if "network" not in self.data or self.data["network"] is None:
            q = self._infer_flowrate()
            calc = OptimumPipeDiameter(flow_rate=q, density=self._get_density())
            d_opt = calc.calculate()
            p = Pipe(nominal_diameter=d_opt, length=L)
            self.data["pipe"] = p
            return p

        # In network mode, each element should define its own geometry.
        raise ValueError("No pipe/diameter provided. In network mode, supply pipe elements inside the network.")

    def _internal_diameter_m(self, pipe: Optional[Pipe]) -> Diameter:
        if pipe:
            if getattr(pipe, "internal_diameter", None) is not None:
                return pipe.internal_diameter
            if getattr(pipe, "nominal_diameter", None) is not None:
                return pipe.nominal_diameter
        d = self.data.get("diameter")
        if d is not None:
            return d if isinstance(d, Diameter) else Diameter(float(d), "mm")
        # As a last resort, compute optimum (single-pipe)
        q = self._infer_flowrate()
        return OptimumPipeDiameter(flow_rate=q, density=self._get_density()).calculate()

    def _maybe_velocity(self, pipe: Pipe) -> Velocity:
        v = self.data.get("velocity")
        if v is not None:
            self._apply_recommended_velocity(pipe, given_velocity=v)
            return v
        q = self._infer_flowrate()
        v = FluidVelocity(volumetric_flow_rate=q, diameter=self._internal_diameter_m(pipe)).calculate()
        self._apply_recommended_velocity(pipe, flowrate=q, computed_velocity=v)
        return v

    def _apply_recommended_velocity(
        self,
        pipe: Pipe,
        flowrate: Optional[VolumetricFlowRate] = None,
        computed_velocity: Optional[Velocity] = None,
        given_velocity: Optional[Velocity] = None,
    ) -> None:
        """If fluid.service_type has a recommended velocity, optionally resize pipe to hit midpoint."""
        service = getattr(self.data.get("fluid"), "service_type", None)
        if not service:
            return
        rec = get_recommended_velocity(service)
        if not rec:
            return

        v_curr = given_velocity or computed_velocity
        if v_curr is None and flowrate is not None:
            v_curr = FluidVelocity(volumetric_flow_rate=flowrate, diameter=self._internal_diameter_m(pipe)).calculate()
        if v_curr is None:
            return

        if isinstance(rec, tuple):
            v_min, v_max = rec
            v_val = v_curr.value if hasattr(v_curr, "value") else float(v_curr)
            if v_val >= v_min and v_val <= v_max:
                return
            target_v = 0.5 * (v_min + v_max)
        else:
            target_v = rec
            v_val = v_curr.value if hasattr(v_curr, "value") else float(v_curr)
            if abs(v_val - target_v) / target_v <= 0.10:
                return

        # resize internal diameter to hit target velocity (kept in mm)
        q = flowrate or self._infer_flowrate()
        from math import pi, sqrt
        A_new = q.value / target_v
        D_new = sqrt(4.0 * A_new / pi)   # meters
        pipe.internal_diameter = Diameter(D_new * 1000.0, "mm")

    # -------------------- Primitive calcs ------------------------------------

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

    def _minor_loss_dp(self, fitting: Fitting, v: Velocity, f: Optional[float] = None, d: Optional[Diameter] = None) -> Pressure:
        """Compute minor loss (supports K or equivalent length Le)."""
        rho = self._get_density()
        v_val = v.value if hasattr(v, "value") else float(v)
        rho_val = rho.value if hasattr(rho, "value") else float(rho)
        d_val = d.value if hasattr(d, "value") else (d if d is not None else None)
        f_val = f.value if hasattr(f, "value") else (f if f is not None else None)

        if getattr(fitting, "K", None) is not None:
            return Pressure(float(fitting.K) * 0.5 * rho_val * v_val * v_val, "Pa")
        if getattr(fitting, "Le", None) is not None:
            if f_val is None or d_val is None:
                raise ValueError("Equivalent length method needs friction factor and diameter.")
            return Pressure(f_val * (fitting.Le / d_val) * 0.5 * rho_val * v_val * v_val, "Pa")
        return Pressure(0.0, "Pa")

    # -------------------- Series/Parallel evaluation -------------------------

    def _pipe_calculation(self, pipe: Pipe, flow_rate: Optional[VolumetricFlowRate]) -> Dict[str, Any]:
        """Compute velocity, Re, f, major DP for a single pipe."""
        # get velocity (if engine has a fixed velocity, use it; else compute from provided flow_rate)
        if self.data.get("velocity") is not None:
            v = self.data["velocity"]
        else:
            q = flow_rate or self._infer_flowrate()
            v = FluidVelocity(volumetric_flow_rate=q, diameter=self._internal_diameter_m(pipe)).calculate()

        Re = self._reynolds(v, pipe)
        f = self._friction_factor(Re, pipe)
        dp_major = self._major_loss_dp(f, v, pipe)

        # Handle any inlined fittings array in the pipe (if your Pipe stores them) OR engine-level single-pipe fittings
        dp_minor = Pressure(0.0, "Pa")
        d = self._internal_diameter_m(pipe)
        fittings: List[Fitting] = []
        # prefer element fittings; else engine-level list in single-pipe mode
        if hasattr(pipe, "fittings") and isinstance(pipe.fittings, list):
            fittings = pipe.fittings
        elif "network" not in self.data and isinstance(self.data.get("fittings"), list):
            fittings = self.data["fittings"]

        for ft in fittings:
            dp_minor += self._minor_loss_dp(ft, v, f=f, d=d)

        return {
            "velocity": v,
            "reynolds": Re,
            "friction_factor": f,
            "pressure_drop": dp_major + dp_minor,
            "major_dp": dp_major,
            "minor_dp": dp_minor,
        }

    def _compute_series(self, series_list: List[Any], flow_rate: Optional[VolumetricFlowRate]) -> Tuple[Pressure, List[Dict[str, Any]]]:
        results: List[Dict[str, Any]] = []
        dp_total = Pressure(0.0, "Pa")

        for element in series_list:
            name = getattr(element, "name", element.__class__.__name__.lower())

            # Pipe
            if isinstance(element, Pipe):
                calc = self._pipe_calculation(element, flow_rate)
                dp_total += calc["pressure_drop"]
                results.append({
                    "type": "pipe",
                    "name": name,
                    "length": element.length,
                    "diameter": self._internal_diameter_m(element),
                    "velocity": calc["velocity"],
                    "reynolds": calc["reynolds"],
                    "friction_factor": calc["friction_factor"],
                    "pressure_drop_Pa": calc["pressure_drop"],
                    "major_dp_Pa": calc["major_dp"],
                    "minor_dp_Pa": calc["minor_dp"],
                })

            # Pump-like (duck-typed by head_gain)
            elif hasattr(element, "head_gain") and element.head_gain is not None:
                gain = element.head_gain.to("Pa")
                dp_total -= gain
                results.append({"type": "pump", "name": name, "head_gain_Pa": gain})

            # Equipment/Vessel/Fitting-like (duck-typed by pressure_drop)
            elif hasattr(element, "pressure_drop"):
                eq_dp = element.pressure_drop.to("Pa") if element.pressure_drop else Pressure(0.0, "Pa")
                dp_total += eq_dp
                results.append({
                    "type": getattr(element, "equipment_type", "equipment"),
                    "name": name,
                    "pressure_drop_Pa": eq_dp
                })

            # Nested network
            elif isinstance(element, PipelineNetwork):
                dp_nested, nested_elems, _ = self._compute_network(element, flow_rate)
                dp_total += dp_nested
                results.extend(nested_elems)

            else:
                raise TypeError(f"Unsupported element type in series: {type(element).__name__}")

            # Optional explicit inlet/outlet pressures on the element
            inlet_p = getattr(element, "inlet_pressure", None)
            outlet_p = getattr(element, "outlet_pressure", None)
            if inlet_p is not None and outlet_p is not None:
                dp_elem = inlet_p.to("Pa") - outlet_p.to("Pa")
                dp_total += dp_elem
                results[-1].update({
                    "inlet_pressure_Pa": inlet_p.to("Pa"),
                    "outlet_pressure_Pa": outlet_p.to("Pa"),
                    "net_dp_from_defined_pressures_Pa": dp_elem
                })

        return dp_total, results

    def _resolve_parallel_flows(self, net: PipelineNetwork, q_m3s: VolumetricFlowRate, branches: List[Any]) -> List[float]:
        split_cfg = (self.data.get("flow_split") or {}).get(net.name)
        n = len(branches)
        if split_cfg is None:
            return [q_m3s.value / n] * n
        vals = [float(x) for x in split_cfg]
        if sum(vals) > 1.5 * q_m3s.value:  # treat as absolute flows
            return vals
        s = sum(vals)
        return [q_m3s.value * (v / s) for v in vals]

    def _compute_network(self, net: PipelineNetwork, q_m3s: Optional[VolumetricFlowRate]) -> Tuple[Pressure, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Returns:
            dp_across: Pressure
            element_results: list
            branch_summaries: list
        """
        if net.connection_type in (None, "series"):
            return (*self._compute_series(net.elements, q_m3s), [])

        # parallel
        branches = net.elements
        q_branches = self._resolve_parallel_flows(net, q_m3s, branches if isinstance(branches, list) else [])
        branch_summaries: List[Dict[str, Any]] = []
        all_results: List[Dict[str, Any]] = []
        dp_across = Pressure(0.0, "Pa")

        for idx, (child, qb) in enumerate(zip(branches, q_branches), start=1):
            q_child = VolumetricFlowRate(qb, "m^3/s")
            if isinstance(child, PipelineNetwork):
                dp_b, elems_b, subs = self._compute_network(child, q_child)
                all_results.extend(elems_b)
                branch_summaries.extend(subs)
            else:
                dp_b, elems_b = self._compute_series([child], q_child)
                all_results.extend(elems_b)

            dp_across = max(dp_across, dp_b)
            branch_summaries.append({
                "parallel_name": net.name,
                "branch_index": idx,
                "flow_m3_s": qb,
                "pressure_drop_Pa": dp_b
            })

        return dp_across, all_results, branch_summaries

    # -------------------- RUN / SUMMARY --------------------------------------

    def run(self) -> PipelineResults:
        """
        Execute the configured calculation and return PipelineResults.
        Also computes residual DP if inlet/outlet pressures and/or available_dp are provided.
        """
        results: Dict[str, Any] = {}
        network = self.data.get("network")

        # Determine inlet flow (for network and diagnostics)
        q_in = None
        try:
            q_in = self._infer_flowrate()
        except Exception:
            pass  # For some pure-pressure driven cases user may not provide flow; but most sizing needs it.

        # NETWORK MODE
        if isinstance(network, PipelineNetwork):
            if q_in is None:
                raise ValueError("Network mode requires flowrate (or sufficient info to infer it).")
            total_dp, element_results, branch_summaries = self._compute_network(network, q_in)
            results["mode"] = "network"
            results["summary"] = {"inlet_flow_m3_s": q_in, "total_pressure_drop_Pa": total_dp}
            results["elements"] = element_results
            if branch_summaries:
                results["parallel_sections"] = branch_summaries
            if hasattr(network, "schematic"):
                results["schematic"] = network.schematic()

        # SINGLE-PIPE MODE
        else:
            pipe = self._ensure_pipe()
            v = self._maybe_velocity(pipe)
            Re = self._reynolds(v, pipe)
            f = self._friction_factor(Re, pipe)
            dp_major = self._major_loss_dp(f, v, pipe)

            # Minor losses (engine-level in single-pipe mode)
            dp_minor = Pressure(0.0, "Pa")
            for ft in self.data.get("fittings", []):
                dp_minor += self._minor_loss_dp(ft, v, f=f, d=self._internal_diameter_m(pipe))

            dp_total = dp_major + dp_minor

            results["mode"] = "single"
            results["pipe"] = {
                "internal_diameter": self._internal_diameter_m(pipe),
                "length": pipe.length,
            }
            results["velocity_m_s"] = v
            results["reynolds_number"] = Re
            results["friction_factor"] = f
            results["pressure_drop_Pa"] = dp_total
            results["major_dp_Pa"] = dp_major
            results["minor_dp_Pa"] = dp_minor

        # Residual / control-valve DP logic (works for both modes)
        inlet_p = self.data.get("inlet_pressure")
        outlet_p_target = self.data.get("target_outlet_pressure") or self.data.get("outlet_pressure")
        available_dp = self.data.get("available_dp")

        if inlet_p is not None and outlet_p_target is not None:
            required_system_dp = inlet_p.to("Pa") - outlet_p_target.to("Pa")
            calc_dp = results["summary"]["total_pressure_drop_Pa"] if results["mode"] == "network" else results["pressure_drop_Pa"]
            residual_dp = required_system_dp - calc_dp
            results["residual_dp_Pa"] = residual_dp

        if available_dp is not None:
            calc_dp = results["summary"]["total_pressure_drop_Pa"] if results["mode"] == "network" else results["pressure_drop_Pa"]
            results["unused_available_dp_Pa"] = available_dp.to("Pa") - calc_dp

        self._results = results
        return PipelineResults(results)

    def summary(self) -> None:
        """Pretty print a concise human-readable summary of the latest run()."""
        if not hasattr(self, "_results") or not self._results:
            raise ValueError("No results. Call run() first.")

        r = self._results
        print("\n=== Pipeline Summary ===")

        if r.get("mode") == "network":
            s = r.get("summary", {})
            q = s.get("inlet_flow_m3_s")
            dp = s.get("total_pressure_drop_Pa")
            if q:  print(f"Inlet Flow: {q.value if hasattr(q,'value') else q:.6f} m³/s")
            if dp: print(f"Total Pressure Drop: {dp.value if hasattr(dp,'value') else dp:.2f} Pa")

            if "parallel_sections" in r:
                print("\n--- Parallel Sections ---")
                for b in r["parallel_sections"]:
                    dpb = b["pressure_drop_Pa"]
                    print(f"  {b['parallel_name']} | Branch {b['branch_index']}: "
                          f"Flow={b['flow_m3_s']:.6f} m³/s, ΔP={dpb.value if hasattr(dpb,'value') else dpb:.2f} Pa")

            if "elements" in r:
                print("\n--- Element Details ---")
                for e in r["elements"]:
                    t = e.get("type", "element")
                    name = e.get("name", t)
                    print(f"  {t.capitalize()}: {name}")
                    if t == "pipe":
                        d = e["diameter"]; v = e["velocity"]; Re = e["reynolds"]; f = e["friction_factor"]; dp = e["pressure_drop_Pa"]
                        print(f"    D: {d.value if hasattr(d,'value') else d:.2f} mm, "
                              f"V: {v.value if hasattr(v,'value') else v:.6f} m/s, "
                              f"Re: {Re.value if hasattr(Re,'value') else Re:.0f}, "
                              f"f: {f.value if hasattr(f,'value') else f:.6f}, "
                              f"ΔP: {dp.value if hasattr(dp,'value') else dp:.2f} Pa")
                    elif t == "pump":
                        gain = e["head_gain_Pa"]
                        print(f"    Head Gain: {gain.value if hasattr(gain,'value') else gain:.2f} Pa")
                    else:
                        dp = e.get("pressure_drop_Pa")
                        if dp:
                            print(f"    ΔP: {dp.value if hasattr(dp,'value') else dp:.2f} Pa")

            if "schematic" in r:
                print("\n=== Schematic ===")
                print(r["schematic"])

        else:
            # Single mode
            p = r.get("pipe", {})
            d = p.get("internal_diameter")
            L = p.get("length")
            v = r.get("velocity_m_s")
            Re = r.get("reynolds_number")
            f = r.get("friction_factor")
            dp = r.get("pressure_drop_Pa")
            dpM = r.get("major_dp_Pa")
            dpm = r.get("minor_dp_Pa")

            print("\n--- Single Pipe ---")
            if d:  print(f"Diameter: {d.value if hasattr(d,'value') else d:.2f} mm")
            if L:  print(f"Length:   {L.value if hasattr(L,'value') else L:.2f} m")
            if v:  print(f"Velocity: {v.value if hasattr(v,'value') else v:.6f} m/s")
            if Re is not None:
                print(f"Reynolds: {Re.value if hasattr(Re,'value') else Re:.0f}")
            if f is not None:
                print(f"f (CW):   {f.value if hasattr(f,'value') else f:.6f}")
            if dp:
                print(f"ΔP total: {dp.value if hasattr(dp,'value') else dp:.2f} Pa"
                      + (f" (Major {dpM.value if hasattr(dpM,'value') else dpM:.2f}, Minor {dpm.value if hasattr(dpm,'value') else dpm:.2f})" if dpM and dpm else ""))

        # Residuals
        resid = r.get("residual_dp_Pa")
        if resid is not None:
            print(f"\nResidual ΔP (e.g., for control valve): {resid.value if hasattr(resid,'value') else resid:.2f} Pa")
        unused = r.get("unused_available_dp_Pa")
        if unused is not None:
            print(f"Unused Available ΔP: {unused.value if hasattr(unused,'value') else unused:.2f} Pa")
