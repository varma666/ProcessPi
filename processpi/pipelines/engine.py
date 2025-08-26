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
    The main simulation engine for ProcessPI, designed to calculate fluid flow
    characteristics and pressure drop in pipeline systems.

    This class provides a high-level, "scikit-learn-like" interface (`fit`/`run`)
    for configuring and executing a pipeline simulation. It can handle both
    single-pipe calculations and complex pipeline networks with series and
    parallel connections.

    Key Features:
    - **Flexible Input**: Accepts various combinations of inputs (e.g., flowrate,
      mass flowrate + density, or velocity + diameter) and infers missing
      parameters.
    - **Single-Pipe Mode**: If no `PipelineNetwork` is provided, it calculates
      the pressure drop for a single pipe run, including major and minor losses.
      It can also automatically size the pipe diameter based on an "optimum"
      velocity if one is not specified.
    - **Network Mode**: Processes complex networks of pipes, fittings, pumps,
      and other equipment connected in series or parallel.
    - **Unit Management**: Integrates with a units system to handle conversions
      and ensure dimensional consistency.
    - **Residual DP Calculation**: Can compute the available pressure drop
      for a control valve or other equipment based on system constraints.

    Example usage:
    >>> engine = PipelineEngine().fit(
    ...       flowrate=VolumetricFlowRate(10, 'm^3/hr'),
    ...       fluid=WaterComponent(),
    ...       pipe=Pipe(internal_diameter=Diameter(150, 'mm'), length=Length(50, 'm'))
    ... ).run()
    >>> engine.print_summary()
    """

    # -------------------- INIT / FIT --------------------
    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the engine. Optionally accepts configuration data directly.

        Args:
            **kwargs: Configuration keyword arguments.
        """
        self.data: Dict[str, Any] = {}
        self._results: Optional[PipelineResults] = None
        # If kwargs are provided, perform the fitting step immediately.
        if kwargs:
            self.fit(**kwargs)

    def fit(self, **kwargs: Any) -> "PipelineEngine":
        """
        Configures the engine with inputs. This method is non-destructive,
        meaning it won't run calculations, only set up the state.

        Args:
            **kwargs: Arbitrary keyword arguments representing the simulation
                      inputs (e.g., `flowrate`, `pipe`, `network`).

        Returns:
            PipelineEngine: The instance itself, for method chaining.
        """
        # Create a shallow copy to prevent the caller's dictionary from being modified.
        self.data = dict(kwargs)

        # Normalize common aliases to a single canonical name.
        # This makes the API more user-friendly and robust to typos.
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

        # Set basic defaults that are not present in the input data.
        self.data.setdefault("flow_split", {})
        self.data.setdefault("fittings", [])
        self.data.setdefault("assume_mm_for_numbers", True)

        # Light validation to fail early on incorrect object types.
        network = self.data.get("network")
        if network is not None and not isinstance(network, PipelineNetwork):
            raise TypeError("`network` must be a PipelineNetwork if provided.")

        return self

    # -------------------- Internal getters / inference ------------------------

    def _get_density(self) -> Density:
        """Retrieves density, preferring direct input, then from a `Component` object."""
        # 1. Check for a direct input value in the engine data.
        if "density" in self.data and self.data["density"] is not None:
            return self.data["density"]
        
        # 2. Check the fluid Component object for a density property.
        if "fluid" in self.data and isinstance(self.data["fluid"], Component):
            fluid = self.data["fluid"]
            if hasattr(fluid, 'density'):
                return fluid.density  # Direct access to the property is all you need.
        
        # 3. Raise an error if no density can be found.
        raise ValueError("Provide density or a fluid Component (with .density()).")
    
    def _get_viscosity(self) -> Viscosity:
        """Retrieves viscosity, preferring direct input, then from a `Component` object."""
        # 1. Check for a direct input value in the engine data.
        if "viscosity" in self.data and self.data["viscosity"] is not None:
            return self.data["viscosity"]
        
        # 2. Check the fluid Component object for a viscosity property.
        if "fluid" in self.data and isinstance(self.data["fluid"], Component):
            fluid = self.data["fluid"]
            if hasattr(fluid, 'viscosity'):
                return fluid.viscosity # Direct access to the property is all you need.
        
        # 3. Raise an error if no viscosity can be found.
        raise ValueError("Provide viscosity or a fluid Component (with .viscosity()).")

    def _infer_flowrate(self) -> VolumetricFlowRate:
        """
        Infers the volumetric flowrate from available input parameters.

        This method checks for the following in order:
        1. An explicit `flowrate` input.
        2. A `mass_flowrate` and `density`.
        3. A `velocity` and a `diameter`.
        """
        # 1) Check for direct flowrate
        q = self.data.get("flowrate")
        if q is not None:
            return q

        # 2) Calculate from mass flow & density
        m = self.data.get("mass_flowrate")
        if m is not None:
            rho = self._get_density()
            # Volumetric flow = mass flow / density. Handles unit objects or raw numbers.
            q_val = (m.value if hasattr(m, "value") else float(m)) / \
                    (rho.value if hasattr(rho, "value") else float(rho))
            q = VolumetricFlowRate(q_val, "m^3/s")
            self.data["flowrate"] = q
            return q

        # 3) Calculate from velocity & diameter
        vel = self.data.get("velocity")
        d = self.data.get("diameter")
        if vel is not None and (d is not None or isinstance(self.data.get("pipe"), Pipe)):
            if d is None:
                d = self._internal_diameter_m(self.data.get("pipe"))

            # Ensure the diameter is a Diameter object. Assume mm if a number is given.
            if not isinstance(d, Diameter):
                if self.data.get("assume_mm_for_numbers", True):
                    d = Diameter(float(d), "mm")
                else:
                    d = Diameter(float(d), "m")
            
            # Use a calculation class to invert velocity to flowrate.
            q = FluidVelocity(volumetric_flow_rate=None, diameter=d, velocity=vel).invert_to_flowrate()
            
            # Fallback calculation if the unit system doesn't handle the inversion perfectly.
            if not isinstance(q, VolumetricFlowRate):
                from math import pi
                v_val = vel.value if hasattr(vel, "value") else float(vel)
                d_m = d.to("m").value
                q = VolumetricFlowRate(v_val * (pi * d_m * d_m / 4.0), "m^3/s")
            
            self.data["flowrate"] = q
            return q

        raise ValueError("Unable to infer flowrate. Provide 'flowrate', or ('mass_flowrate' & 'density'), or ('velocity' & 'diameter').")

    def _ensure_pipe(self) -> Pipe:
        """
        Returns an existing Pipe object or constructs a new one.

        In single-pipe mode, if no `Pipe` is given but `diameter` and `length`
        are, a `Pipe` object is created. If only `flowrate` is given, it
        calculates an "optimum" diameter and creates the `Pipe`.
        """
        p = self.data.get("pipe")
        if isinstance(p, Pipe):
            return p

        # If diameter and length are provided, build a pipe from them.
        d = self.data.get("diameter")
        L = self.data.get("length") or Length(1.0, "m")
        if d is not None:
            if not isinstance(d, Diameter):
                d = Diameter(float(d), "mm" if self.data.get("assume_mm_for_numbers", True) else "m")
            p = Pipe(internal_diameter=d, length=L)
            self.data["pipe"] = p
            return p

        # If a network is not provided (single-pipe mode) and no diameter is given,
        # compute an optimum diameter based on flowrate and density.
        if "network" not in self.data or self.data["network"] is None:
            q = self._infer_flowrate()
            calc = OptimumPipeDiameter(flow_rate=q, density=self._get_density())
            d_opt = calc.calculate()
            p = Pipe(nominal_diameter=d_opt, length=L)
            self.data["pipe"] = p
            return p

        raise ValueError("No pipe/diameter provided. In network mode, supply pipe elements inside the network.")

    def _internal_diameter_m(self, pipe: Optional[Pipe] = None) -> Diameter:
        """
        Fetches the internal diameter in meters from a pipe object or the
        engine's data. Falls back to an an optimum diameter if necessary.
        """
        pipe = pipe or self.data.get("pipe")
        if pipe:
            if getattr(pipe, "internal_diameter", None) is not None:
                return pipe.internal_diameter
            if getattr(pipe, "nominal_diameter", None) is not None:
                return pipe.nominal_diameter
        
        d = self.data.get("diameter")
        if d is not None:
            # Assumes numbers are in mm unless configured otherwise.
            return d if isinstance(d, Diameter) else Diameter(float(d), "mm")

        # As a last resort, compute optimum diameter for a single pipe.
        q = self._infer_flowrate()
        return OptimumPipeDiameter(flow_rate=q, density=self._get_density()).calculate()

    def _maybe_velocity(self, pipe: Pipe) -> Velocity:
        """
        Returns a pre-defined velocity if available; otherwise, computes it.
        It also checks against recommended velocities and can resize the pipe
        if the fluid service type has a target velocity.
        """
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
        """
        Internal helper to check if the current velocity is within a recommended
        range for the fluid's service type. If not, it modifies the pipe's
        internal diameter to achieve the midpoint velocity.
        """
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

        # Check if the velocity is within the recommended range.
        if isinstance(rec, tuple):
            v_min, v_max = rec
            v_val = v_curr.value if hasattr(v_curr, "value") else float(v_curr)
            if v_min <= v_val <= v_max:
                return
            target_v = 0.5 * (v_min + v_max)
        else: # Single recommended velocity
            target_v = rec
            v_val = v_curr.value if hasattr(v_curr, "value") else float(v_curr)
            if abs(v_val - target_v) / target_v <= 0.10: # within 10% tolerance
                return

        # Resize internal diameter to hit the target velocity.
        q = flowrate or self._infer_flowrate()
        from math import pi, sqrt
        A_new = q.value / target_v
        D_new = sqrt(4.0 * A_new / pi)  # diameter in meters
        pipe.internal_diameter = Diameter(D_new * 1000.0, "mm")

    # --- Unit helpers (inside PipelineEngine) ---
    def _as_pressure(self, maybe_pressure: Any, default_unit: str = "Pa") -> Optional[Pressure]:
        """Accepts a Pressure object, a number, or None and returns a Pressure object."""
        if maybe_pressure is None:
            return None
        if isinstance(maybe_pressure, Pressure):
            return maybe_pressure
        return Pressure(float(maybe_pressure), default_unit)
    
    def _pump_gain_pa(self, pump: Any) -> Pressure:
        """
        Converts a Pump's head or pressure difference into a pressure gain in Pa.
        This uses a simple hierarchy: `inlet_pressure`/`outlet_pressure` first,
        then `head`, and finally a default of zero.
        """
        rho = getattr(pump, "density", None) or self._get_density().value
        g = 9.81
        pin = getattr(pump, "inlet_pressure", None)
        pout = getattr(pump, "outlet_pressure", None)
        if pin is not None and pout is not None:
            return self._as_pressure(pout).to("Pa") - self._as_pressure(pin).to("Pa")
        
        head = getattr(pump, "head", 0.0) or 0.0
        return Pressure(rho * g * float(head), "Pa")
    
    def _equipment_dp_pa(self, eq: Any) -> Pressure:
        """Converts an Equipment's pressure drop (assumed to be in bar) to Pa."""
        dp_bar = getattr(eq, "pressure_drop", 0.0) or 0.0
        return Pressure(float(dp_bar), "bar").to("Pa")
    
    def _fitting_dp_pa(self, fitting: Fitting, v: Velocity, f: Optional[float], d: Diameter) -> Pressure:
        """
        Computes the pressure drop for a fitting using either its K-factor
        (preferred) or equivalent length (`Le`) method.
        """
        rho = self._get_density().value
        v_val = v.value if hasattr(v, "value") else float(v)
        
        # Try K-factor method first (0.5 * rho * v^2 * K)
        Ktot = getattr(fitting, "K_factor", None) or getattr(fitting, "total_K", None)
        if Ktot is not None:
            try:
                Ktot = float(Ktot)
                return Pressure(0.5 * rho * v_val * v_val * Ktot, "Pa")
            except (ValueError, TypeError):
                # Fall through to the next method if K is not a number
                pass
        
        # Fallback to equivalent length method (f * (Le/D) * 0.5 * rho * v^2)
        Le = getattr(fitting, "Le", None) or getattr(fitting, "equivalent_length", None)
        if Le is not None:
            if f is None:
                # Recompute friction factor if not provided (needed for Le/D method).
                Re = self._reynolds(v, type("Tmp", (), {"roughness": 0.0, "length": Length(1.0, "m")})())
                f_val = self._friction_factor(Re, type("Tmp", (), {"roughness": 0.0})())
            else:
                f_val = f
            
            d_m = d.to("m").value
            return Pressure(float(f_val) * (float(Le) / d_m) * 0.5 * rho * v_val * v_val, "Pa")
        
        # Neither K nor Le available, so no minor loss is accounted for.
        return Pressure(0.0, "Pa")


    # -------------------- Primitive calcs ------------------------------------

    def _reynolds(self, v: Velocity, pipe: Pipe) -> float:
        """Calculates the Reynolds Number for a given pipe and velocity."""
        return ReynoldsNumber(
            density=self._get_density(),
            velocity=v,
            diameter=self._internal_diameter_m(pipe),
            viscosity=self._get_viscosity(),
        ).calculate()

    def _friction_factor(self, Re: float, pipe: Pipe) -> float:
        """Calculates the Darcy friction factor using the Colebrook-White equation."""
        return ColebrookWhite(
            reynolds_number=Re,
            roughness=float(pipe.roughness),
            diameter=self._internal_diameter_m(pipe),
        ).calculate()

    def _major_loss_dp(self, f: float, v: Velocity, pipe: Pipe) -> Pressure:
        """Calculates the major pressure drop (due to pipe friction) using the Darcy-Weisbach equation."""
        return PressureDropDarcy(
            friction_factor=f,
            length=pipe.length,
            diameter=self._internal_diameter_m(pipe),
            density=self._get_density(),
            velocity=v,
        ).calculate()

    def _minor_loss_dp(self, fitting: Fitting, v: Velocity, f: Optional[float] = None, d: Optional[Diameter] = None) -> Pressure:
        """
        Computes the minor pressure loss for a fitting.
        This is a re-implementation of _fitting_dp_pa with slightly different
        logic to handle the `fitting.K` and `fitting.Le` attributes directly.
        """
        rho = self._get_density()
        v_val = v.value if hasattr(v, "value") else float(v)
        rho_val = rho.value if hasattr(rho, "value") else float(rho)

        # Use K-factor first if it exists.
        if hasattr(fitting, "K") and fitting.K is not None:
            return Pressure(float(fitting.K) * 0.5 * rho_val * v_val * v_val, "Pa")
        
        # Fallback to equivalent length.
        if hasattr(fitting, "Le") and fitting.Le is not None:
            if f is None or d is None:
                raise ValueError("Equivalent length method needs friction factor and diameter.")
            d_val = d.value if hasattr(d, "value") else float(d)
            f_val = f.value if hasattr(f, "value") else float(f)
            return Pressure(f_val * (fitting.Le / d_val) * 0.5 * rho_val * v_val * v_val, "Pa")
        
        return Pressure(0.0, "Pa")


    # -------------------- Series/Parallel evaluation -------------------------

    def _pipe_calculation(self, pipe: Pipe, flow_rate: Optional[VolumetricFlowRate]) -> Dict[str, Any]:
        """
        Calculates fluid dynamics and pressure drop for a single pipe.
        This helper function is used by both single-pipe and network modes.
        """
        # Determine velocity: use fixed velocity from engine or compute it.
        v = self.data.get("velocity")
        if v is None:
            q = flow_rate or self._infer_flowrate()
            v = FluidVelocity(volumetric_flow_rate=q, diameter=self._internal_diameter_m(pipe)).calculate()

        # Perform the core fluid calculations.
        Re = self._reynolds(v, pipe)
        f = self._friction_factor(Re, pipe)
        dp_major = self._major_loss_dp(f, v, pipe)

        # Handle minor losses for fittings associated with this pipe.
        dp_minor = Pressure(0.0, "Pa")
        d = self._internal_diameter_m(pipe)
        fittings: List[Fitting] = []
        if hasattr(pipe, "fittings") and isinstance(pipe.fittings, list):
            fittings = pipe.fittings
        elif "network" not in self.data and isinstance(self.data.get("fittings"), list):
            # In single-pipe mode, fittings can be passed at the top level.
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
                dp_total += calc["pressure_drop"]
                current_d = self._internal_diameter_m(element)
                current_v = calc["velocity"]
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
            
            # Pump (energy gain)
            elif element.__class__.__name__ == "Pump":
                pump_gain = self._pump_gain_pa(element)
                dp_total -= pump_gain  # Subtract pump gain from total pressure drop.
                results.append({
                    "type": "pump",
                    "name": element_name,
                    "head_gain_Pa": pump_gain,
                    "head_m": getattr(element, "head", None),
                    "efficiency": getattr(element, "efficiency", None),
                })
            
            # Equipment (e.g., heat exchanger, valve)
            elif element.__class__.__name__ == "Equipment":
                eq_dp = self._equipment_dp_pa(element)
                dp_total += eq_dp
                results.append({
                    "type": "equipment",
                    "name": getattr(element, "name", element_name),
                    "pressure_drop_Pa": eq_dp,
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
                dp_total += dp_fit
                results.append({
                    "type": "fitting",
                    "name": element_name,
                    "pressure_drop_Pa": dp_fit,
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
                dp_total += dp_element
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

    def _compute_network(self, net: PipelineNetwork, q_m3s: Optional[VolumetricFlowRate]) -> Tuple[Pressure, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Recursively computes the pressure drop across a network.
        Handles both series and parallel connections.
        
        Returns:
            dp_across: The total pressure drop across the network.
            element_results: Detailed results for each element.
            branch_summaries: Summaries for each parallel branch.
        """
        # If the network is in series mode, call the series computation.
        if net.connection_type in (None, "series"):
            return (*self._compute_series(net.elements, q_m3s, self.data.get("fluid")), [])

        # If the network is in parallel mode, calculate pressure drop across all branches.
        branches = net.elements
        q_branches = self._resolve_parallel_flows(net, q_m3s, branches if isinstance(branches, list) else [])
        branch_summaries: List[Dict[str, Any]] = []
        all_results: List[Dict[str, Any]] = []
        dp_across = Pressure(0.0, "Pa")

        for idx, (child, qb) in enumerate(zip(branches, q_branches), start=1):
            q_child = VolumetricFlowRate(qb, "m^3/s")
            
            # Recursively call this method if a child is also a network.
            if isinstance(child, PipelineNetwork):
                dp_b, elems_b, subs = self._compute_network(child, q_child)
                all_results.extend(elems_b)
                branch_summaries.extend(subs)
            else:
                # Calculate for a single branch (which is a series of elements).
                dp_b, elems_b = self._compute_series([child], q_child, self.data.get("fluid"))
                all_results.extend(elems_b)

            # In parallel, the overall pressure drop is the maximum of all branches.
            dp_across = max(dp_across, dp_b)
            
            # Store summary data for each branch.
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
        Executes the fluid dynamic calculations based on the fitted inputs.
        This is the main public method that initiates the simulation.
        
        Returns:
            PipelineResults: A data transfer object containing all
                             the calculation results.
        """
        results: Dict[str, Any] = {}
        network = self.data.get("network")

        # Get the total inlet flow. This is a common starting point for all calcs.
        q_in: Optional[VolumetricFlowRate] = None
        try:
            q_in = self._infer_flowrate()
        except ValueError:
            # In some cases, like pure pressure-driven flow, flowrate may not be given.
            pass

        # Execute calculation based on whether a network is provided.
        if isinstance(network, PipelineNetwork):
            # Network mode
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

        else:
            # Single-pipe mode
            pipe = self._ensure_pipe()
            v = self._maybe_velocity(pipe)
            Re = self._reynolds(v, pipe)
            f = self._friction_factor(Re, pipe)
            dp_major = self._major_loss_dp(f, v, pipe)

            # Minor losses from the engine-level fittings list.
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

        # --- Post-calculation analysis (e.g., residual DP for control valves) ---
        inlet_p = self.data.get("inlet_pressure")
        outlet_p_target = self.data.get("target_outlet_pressure") or self.data.get("outlet_pressure")
        available_dp = self.data.get("available_dp")

        # Case 1: Inlet and outlet pressures are given. Calculate total system DP.
        if inlet_p is not None and outlet_p_target is not None:
            inlet_p = self._as_pressure(inlet_p).to("Pa")
            outlet_p_target = self._as_pressure(outlet_p_target).to("Pa")
            # Calculate the total change across the system from boundary conditions.
            system_dp_pa = inlet_p - outlet_p_target
            
            # Any difference is the "unaccounted" or residual DP.
            residual_dp = system_dp_pa - total_dp
            results["residual_dp_Pa"] = residual_dp
            results["total_system_dp_from_boundaries"] = system_dp_pa
            # For a control valve, the residual DP is what's "available" for it.
            # We add a specific field for clarity.
            results["available_dp_for_valve_Pa"] = residual_dp

        # Case 2: Only available DP for a valve is given.
        elif available_dp is not None:
            available_dp = self._as_pressure(available_dp).to("Pa")
            required_dp = total_dp
            results["required_dp_Pa"] = required_dp
            results["available_dp_for_valve_Pa"] = available_dp
            # Check if the available DP is sufficient.
            if required_dp > available_dp:
                results["warnings"] = "Required DP exceeds available DP."
        
        # Store the results and return the DTO.
        self._results = PipelineResults(results)
        return self._results

    def summary(self) -> None:
        """
        Prints a concise, human-readable summary of the last simulation run.
        Requires that `run()` has been called.
        """
        if self._results is None:
            raise ValueError("No results to summarize. Call run() first.")
        self._results.summary()
