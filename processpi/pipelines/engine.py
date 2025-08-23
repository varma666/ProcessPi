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

    # --- Unit helpers (inside PipelineEngine) ---
    def _as_pressure(self, maybe_pressure, default_unit="Pa"):
        """Accept Pressure, float, or None and return a Pressure (or None)."""
        if maybe_pressure is None:
            return None
        if isinstance(maybe_pressure, Pressure):
            return maybe_pressure
        # assume float in default_unit
        return Pressure(float(maybe_pressure), default_unit)
    
    def _pump_gain_pa(self, pump) -> Pressure:
        """
        Convert your Pump (head in m or pressures) to a pressure 'gain' (Pa).
        Priority:
          - If both inlet/outlet pressures exist -> use their difference
          - Else if head exists -> rho*g*H
          - Else -> 0 Pa
        """
        rho = getattr(pump, "density", None) or self._get_density().value
        g = 9.81
        pin = getattr(pump, "inlet_pressure", None)
        pout = getattr(pump, "outlet_pressure", None)
        if pin is not None and pout is not None:
            return (self._as_pressure(pout).to("Pa") - self._as_pressure(pin).to("Pa"))
        head = getattr(pump, "head", 0.0) or 0.0
        return Pressure(rho * g * float(head), "Pa")
    
    def _equipment_dp_pa(self, eq) -> Pressure:
        """
        Your Equipment stores pressure_drop in 'bar' (float).
        Convert to Pressure in Pa.
        """
        dp_bar = getattr(eq, "pressure_drop", 0.0) or 0.0
        return Pressure(float(dp_bar), "bar").to("Pa")
    
    def _fitting_dp_pa(self, fitting, v: Velocity, f: Optional[float], d: Diameter) -> Pressure:
        """
        Compute minor loss from your Fitting using total_K() or equivalent_length().
        """
        rho = self._get_density().value
        v_val = v.value if hasattr(v, "value") else float(v)
        # Try K-method first
        Ktot = None
        try:
            Ktot = fitting.total_K()
        except Exception:
            Ktot = None
        if Ktot is not None:
            return Pressure(0.5 * rho * v_val * v_val * float(Ktot), "Pa")
    
        # Fallback: equivalent length method
        Le = None
        try:
            Le = fitting.equivalent_length()
        except Exception:
            Le = None
        if Le is not None:
            # We need friction factor for Le/D method. If not passed, recompute here.
            if f is None:
                # compute f using pipe diameter 'd'
                Re = self._reynolds(v, type("Tmp", (), {"roughness": 0.0, "length": Length(1.0, "m")})())  # roughness ignored here
                f_val = self._friction_factor(Re, type("Tmp", (), {"roughness": 0.0})())
            else:
                f_val = f
            d_m = d.to("m").value
            return Pressure(float(f_val) * (float(Le) / d_m) * 0.5 * rho * v_val * v_val, "Pa")
    
        # Neither K nor Le available => no minor loss accounted
        return Pressure(0.0, "Pa")


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

    def _compute_series(self, series_list, flow_rate, fluid):
        results = []
        dp_total = Pressure(0, "Pa")
    
        # Precompute a working velocity/diameter if there is at least one pipe
        # (needed for fittings). We update this on the fly for each pipe.
        current_d: Optional[Diameter] = None
        current_v: Optional[Velocity] = None
        current_f: Optional[float] = None
    
        for element in series_list:
            element_name = getattr(element, "name", getattr(element, "fitting_type", element.__class__.__name__.lower()))
    
            # --- Pipe ---
            if isinstance(element, Pipe):
                calc = self._pipe_calculation(element, flow_rate)
                dp_total += calc["pressure_drop"]
                current_d = self._internal_diameter_m(element)
                current_v = calc["velocity"]
                # friction factor for this pipe (useful for subsequent fittings via Le/D)
                current_f = calc["friction_factor"]
    
                results.append({
                    "type": "pipe",
                    "name": element_name,
                    "length": element.length,
                    "diameter": current_d,
                    "pressure_drop_Pa": calc["pressure_drop"],
                    "reynolds": calc["reynolds"],
                    "friction_factor": current_f,
                    "velocity": current_v,
                })
    
            # --- Pump (your Pump class) ---
            elif element.__class__.__name__ == "Pump":
                pump_gain = self._pump_gain_pa(element)  # Pa
                dp_total -= pump_gain  # pump adds energy
                results.append({
                    "type": "pump",
                    "name": element_name,
                    "head_gain_Pa": pump_gain,
                    "head_m": getattr(element, "head", None),
                    "efficiency": getattr(element, "efficiency", None),
                })
    
            # --- Equipment (your Equipment class with pressure_drop in bar) ---
            elif element.__class__.__name__ == "Equipment":
                eq_dp = self._equipment_dp_pa(element)
                dp_total += eq_dp
                results.append({
                    "type": "equipment",
                    "name": getattr(element, "name", element_name),
                    "pressure_drop_Pa": eq_dp,
                })
    
            # --- Fitting (minor loss) ---
            elif isinstance(element, Fitting):
                # We need a velocity & diameter context. If none yet, try to derive from engine-level flowrate.
                if current_d is None or current_v is None:
                    # try derive from any pipe dimension on fitting or engine diameter
                    d_for_fit = None
                    if hasattr(element, "diameter") and element.diameter:
                        d_for_fit = element.diameter if isinstance(element.diameter, Diameter) else Diameter(float(element.diameter), "mm")
                    else:
                        d_for_fit = self._internal_diameter_m()  # could compute via optimum if single-line
                    q = flow_rate or self._maybe_flowrate()
                    current_v = FluidVelocity(volumetric_flow_rate=q, diameter=d_for_fit).calculate()
                    current_d = d_for_fit
                    # friction factor unknown; pass None (method will recompute if needed)
                    current_f = None
    
                dp_fit = self._fitting_dp_pa(element, current_v, current_f, current_d)
                dp_total += dp_fit
                results.append({
                    "type": "fitting",
                    "name": element_name,
                    "pressure_drop_Pa": dp_fit,
                    "using": "K" if element.total_K() is not None else ("Le" if element.equivalent_length() is not None else "none"),
                    "quantity": getattr(element, "quantity", 1),
                })
    
            # --- Vessel (no default ΔP; acts as connection/boundary unless later extended) ---
            elif element.__class__.__name__ == "Vessel":
                # treat as zero-ΔP pass-through unless you decide to add a vessel ΔP later
                results.append({
                    "type": "vessel",
                    "name": getattr(element, "name", element_name),
                    "pressure_drop_Pa": Pressure(0.0, "Pa"),
                    "note": "No default ΔP; boundary/holdup element.",
                })
    
            # --- Nested Networks (unchanged) ---
            elif isinstance(element, PipelineNetwork):
                # Handled by _compute_network (this path normally won't show up here)
                raise TypeError("Nested networks should be handled in _compute_network, not _compute_series.")
    
            else:
                raise TypeError(f"Unsupported element type: {type(element).__name__}")
    
            # --- Optional inlet/outlet pressures on any element (duck-typed) ---
            inlet_p = getattr(element, "inlet_pressure", None)
            outlet_p = getattr(element, "outlet_pressure", None)
            if inlet_p is not None and outlet_p is not None:
                dp_element = self._as_pressure(inlet_p).to("Pa") - self._as_pressure(outlet_p).to("Pa")
                dp_total += dp_element
                results[-1].update({
                    "inlet_pressure_Pa": self._as_pressure(inlet_p).to("Pa"),
                    "outlet_pressure_Pa": self._as_pressure(outlet_p).to("Pa"),
                    "net_dp_from_defined_pressures_Pa": dp_element
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
