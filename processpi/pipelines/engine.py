# processpi/pipelines/engine.py
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union

from ..units import (
    Diameter, Length, Pressure, Density, Viscosity, VolumetricFlowRate, Velocity, MassFlowRate
)
from .pipelineresults import PipelineResults
from .nozzle import Nozzle
from ..components import Component
from .standards import (
    get_k_factor, get_roughness, list_available_pipe_diameters, get_standard_pipe_data, get_recommended_velocity, get_standard_pipe_schedules
)
from .pipes import Pipe
from .fittings import Fitting
from .equipment import Equipment
from .network import PipelineNetwork
from .piping_costs import PipeCostModel
from ..calculations.fluids import (
    FluidVelocity, ReynoldsNumber, PressureDropDarcy, OptimumPipeDiameter, PressureDropFanning, ColebrookWhite
)


class PipelineEngine:
    """
    Main simulation engine for ProcessPI. Supports single-pipe and network calculations.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.data: Dict[str, Any] = {}
        self._results: Optional[PipelineResults] = None
        if kwargs:
            self.fit(**kwargs)

    def fit(self, **kwargs: Any) -> "PipelineEngine":
        """
        Configures the engine with inputs. Does not run calculations.
        Adds validation for mass/volumetric flow rates.
        """
        self.data = dict(kwargs)

        # Alias normalization
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

        # Default fields
        self.data.setdefault("flow_split", {})
        self.data.setdefault("fittings", [])
        self.data.setdefault("assume_mm_for_numbers", True)

        # Type validation
        network = self.data.get("network")
        if network is not None and not isinstance(network, PipelineNetwork):
            raise TypeError("`network` must be a PipelineNetwork if provided.")

        # ------------------ Mass/Volumetric Flow Validation ------------------
        flowrate = self.data.get("flowrate")
        mass_flow = self.data.get("mass_flowrate")

        # If both are provided, check consistency
        if flowrate and mass_flow:
            rho = self.data.get("density")
            if not rho and "fluid" in self.data and isinstance(self.data["fluid"], Component):
                rho = self.data["fluid"].density()
            if rho:
                q_val = flowrate.value if hasattr(flowrate, "value") else float(flowrate)
                m_val = mass_flow.value if hasattr(mass_flow, "value") else float(mass_flow)
                rho_val = rho.value if hasattr(rho, "value") else float(rho)
                expected_m = q_val * rho_val
                if abs(expected_m - m_val) / max(expected_m, m_val) > 0.01:
                    raise ValueError(
                        f"Inconsistent flow rates: mass_flow={m_val} kg/s, "
                        f"flowrate={q_val} m3/s, density={rho_val} kg/m3"
                    )

        # Ensure positive values
        if flowrate and ((flowrate.value if hasattr(flowrate, "value") else float(flowrate)) <= 0):
            raise ValueError("Volumetric flowrate must be positive.")
        if mass_flow and ((mass_flow.value if hasattr(mass_flow, "value") else float(mass_flow)) <= 0):
            raise ValueError("Mass flowrate must be positive.")
        print(self.data)
        return self

    # -------------------- Internal getters / inference ------------------------
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

    def _infer_flowrate(self) -> VolumetricFlowRate:
        """
        Infers volumetric flowrate from:
        1) Provided flowrate
        2) Mass flowrate & density
        3) Velocity & diameter
        """
        q = self.data.get("flowrate")
        if q is not None:
            return q

        m = self.data.get("mass_flowrate")
        if m is not None:
            rho = self._get_density()
            q_val = (m.value if hasattr(m, "value") else float(m)) / \
                    (rho.value if hasattr(rho, "value") else float(rho))
            q = VolumetricFlowRate(q_val, "m3/s")
            self.data["flowrate"] = q
            return q

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
                q = VolumetricFlowRate(vel.value * math.pi * (d.to("m").value ** 2) / 4, "m^3/s")
            self.data["flowrate"] = q
            return q

        raise ValueError("Unable to infer flowrate. Provide 'flowrate', or ('mass_flowrate' & 'density'), or ('velocity' & 'diameter').")


    def _ensure_pipe(self) -> Pipe:
        """
        Returns an existing Pipe object or constructs a new one.

        Handles single-pipe mode:
        - If `Pipe` is given, returns it.
        - If `diameter` and `length` are given, constructs a Pipe.
        - If only flowrate and density are available, calculates optimum diameter.
        """
        p = self.data.get("pipe")
        if isinstance(p, Pipe):
            return p

        # 1. Build from given diameter & length
        d = self.data.get("diameter")
        print(f"Diameter provided: {d}")
        L = self.data.get("length") or Length(1.0, "m")
        if d is not None:
            if not isinstance(d, Diameter):
                # Assume mm unless flagged otherwise
                d = Diameter(
                    float(d),
                    "mm" if self.data.get("assume_mm_for_numbers", True) else "m"
                )
            p = Pipe(name="Main Pipe", internal_diameter=d, length=L)
            self.data["pipe"] = p
            print(f"Pipe created: {p}")
            return p

        # 2. Calculate optimum diameter if no pipe/diameter provided
        if self.data.get("network") is None:
            q = self._infer_flowrate()
            calc = OptimumPipeDiameter(flow_rate=q, density=self._get_density())
            d_opt = calc.calculate()
            p = Pipe(name="Main Pipe", nominal_diameter=d_opt, length=L)
            self.data["pipe"] = p
            return p

        # 3. Network mode requires pipes inside the network
        raise ValueError(
            "No pipe/diameter provided. In network mode, supply pipe elements inside the network."
        )

    def _internal_diameter_m(self, pipe: Optional[Pipe] = None) -> Diameter:
        """
        Returns the pipe's internal diameter in meters as a Diameter object.

        Priority:
        1. pipe.internal_diameter
        2. pipe.nominal_diameter
        3. engine data['diameter']
        4. Compute optimum diameter from flowrate/density
        """
        pipe = pipe or self.data.get("pipe")

        # 1. Pipe object
        if pipe:
            if getattr(pipe, "internal_diameter", None) is not None:
                d = pipe.internal_diameter
                return d if isinstance(d, Diameter) else Diameter(float(d), "m")
            if getattr(pipe, "nominal_diameter", None) is not None:
                d = pipe.nominal_diameter
                return d if isinstance(d, Diameter) else Diameter(float(d), "m")

        # 2. Engine data
        d = self.data.get("diameter")
        if d is not None:
            return d if isinstance(d, Diameter) else Diameter(float(d), "mm" if self.data.get("assume_mm_for_numbers", True) else "m")

        # 3. Fallback: compute optimum for single pipe
        q = self._infer_flowrate()
        return OptimumPipeDiameter(flow_rate=q, density=self._get_density()).calculate()

    def _maybe_velocity(self, pipe: Pipe) -> Velocity:
        """
        Returns a pre-defined velocity if available; otherwise, computes it.

        Works with Pressure/FlowRate objects and applies recommended velocity
        for the fluid service type.
        """
        v = self.data.get("velocity")
        if v is not None:
            # Already a Velocity object or a number (convert if needed)
            if not isinstance(v, Velocity):
                v = Velocity(float(v), "m/s")
            self._apply_recommended_velocity(pipe, given_velocity=v)
            return v

        # Infer flowrate
        q = self._infer_flowrate()
        # Calculate velocity from volumetric flowrate and internal pipe diameter
        v = FluidVelocity(
            volumetric_flow_rate=q,
            diameter=self._internal_diameter_m(pipe)
        ).calculate()
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

    def _solve_for_diameter(self, available_dp: Union[Pressure, float], **kwargs: Any) -> PipelineResults:
        """
        Determines the smallest standard pipe size that satisfies the available pressure drop
        for the given flow conditions (mass or volumetric flow rate).

        Parameters
        ----------
        available_dp : Pressure or float
            Maximum allowable pressure drop.
        kwargs : dict
            Additional parameters: mass_flowrate, flowrate, length, density, viscosity, material, fittings.

        Returns
        -------
        PipelineResults
            Contains the selected pipe, pressure drop, and solution info.
        """
        # ----------------- Step 1: Convert available DP to Pa -----------------
        if isinstance(available_dp, Pressure):
            available_dp_pa = available_dp.to("Pa").value
        else:
            available_dp_pa = float(available_dp)

        # ----------------- Step 2: Ensure flowrate in volumetric units -----------------
        flowrate = kwargs.get("flowrate")
        if flowrate is None and "mass_flowrate" in kwargs:
            rho = kwargs.get("density", self._get_density())
            flowrate = VolumetricFlowRate.from_mass_flow(kwargs["mass_flowrate"], rho)

        if flowrate is None:
            raise ValueError("Flowrate or mass flowrate must be provided for diameter calculation.")

        # ----------------- Step 3: Loop over standard diameters -----------------
        for nominal_d in list_available_pipe_diameters():
            for schedule in get_standard_pipe_schedules():
                try:
                    pipe_data = get_standard_pipe_data(nominal_d, schedule)
                except ValueError:
                    continue

                internal_d = pipe_data["internal_diameter"]
                pipe_instance = Pipe(
                    name=f"Pipe {nominal_d}-{schedule}",
                    nominal_diameter=nominal_d,
                    internal_diameter=internal_d,
                    schedule=schedule,
                    length=kwargs.get("length", Length(1, "m")),
                    material=kwargs.get("material", "CS")
                )

                # ----------------- Step 4: Run pipe DP calculation -----------------
                pipeline_data = self._pipe_calculation(
                    pipe_instance,
                    flow_rate=flowrate,
                    fittings=kwargs.get("fittings", []),
                    equipment=kwargs.get("equipment", [])
                )

                # ----------------- Step 5: Check DP against available -----------------
                dp = pipeline_data.get("pressure_drop")
                dp_val = dp.to("Pa").value if isinstance(dp, Pressure) else float(dp)

                if dp_val <= available_dp_pa:
                    results = PipelineResults(pipeline_data)
                    results.add_info("solution_found", True)
                    results.add_info("selected_nominal_diameter", nominal_d)
                    results.add_info("selected_schedule", schedule)
                    results.add_info("calculated_pressure_drop", dp)
                    results.add_info("available_pressure_drop", available_dp)
                    return results

        raise ValueError(
            "No standard pipe size found that satisfies the available pressure drop for the given flow conditions."
        )

    def _optimize_network_for_size(self, network: PipelineNetwork, available_dp: Pressure) -> PipelineResults:
        """
        Internal helper method to optimize pipe sizes in a network.
        It uses an iterative approach to find the most cost-effective solution
        that meets the pressure drop constraint.
        """
        cost_model = self.data.get("cost_model") or PipeCostModel.default_steel_model()
        max_iterations = 100
        
        pipes_to_optimize: List[Pipe] = [
            p for p in network.get_all_pipes() if p.nominal_diameter is None
        ]
        
        if not pipes_to_optimize:
            raise ValueError("No pipes found in the network to optimize. All pipes have a specified diameter.")

        standard_diameters_in = [d.to('in').value for d in list_available_pipe_diameters()]
        
        initial_diameter_in = standard_diameters_in[0]
        for p in pipes_to_optimize:
            p.nominal_diameter = Diameter(initial_diameter_in, 'in')
        
        calculated_dp = float('inf')
        iterations = 0

        # Main Optimization Loop
        while calculated_dp > available_dp.to('Pa').value and iterations < max_iterations:
            results = self.fit(network=network).run()
            calculated_dp = results.get_summary()['total_pressure_drop_Pa']
            
            if calculated_dp > available_dp.to('Pa').value:
                # Find the most hydraulically stressed pipe and increase its size
                max_dp_pipe = None
                max_dp = -1
                pipe_summary = results.get_summary().get('pipes_summary', [])
                
                for pipe_data in pipe_summary:
                    if pipe_data.get('pressure_drop', 0) > max_dp and pipe_data.get('diameter', 0) in standard_diameters_in:
                        max_dp = pipe_data['pressure_drop']
                        max_dp_pipe = pipe_data
                
                if max_dp_pipe:
                    target_pipe = next((p for p in pipes_to_optimize if p.name == max_dp_pipe['name']), None)
                    if target_pipe:
                        current_dia_in = target_pipe.nominal_diameter.to('in').value
                        try:
                            current_idx = standard_diameters_in.index(current_dia_in)
                            if current_idx + 1 < len(standard_diameters_in):
                                target_pipe.nominal_diameter = Diameter(standard_diameters_in[current_idx + 1], 'in')
                            else:
                                raise ValueError("Could not find a solution. Even the largest pipe size is insufficient.")
                        except ValueError:
                            # Diameter not in standard list, increase to next standard size
                            next_dia_in = next((d for d in standard_diameters_in if d > current_dia_in), None)
                            if next_dia_in:
                                target_pipe.nominal_diameter = Diameter(next_dia_in, 'in')
                            else:
                                raise ValueError("Could not find a solution. Even the largest pipe size is insufficient.")
                else:
                    raise ValueError("Could not find a solution. All pipes are at max size or issue with data.")
            
            iterations += 1

        if calculated_dp > available_dp.to('Pa').value:
             raise ValueError(f"Failed to converge on a solution within {max_iterations} iterations. Final DP: {calculated_dp} Pa.")

        # Final check and return results
        final_results = self.fit(network=network).run()
        final_results.add_info("Optimization Results", {
            "Total Cost": cost_model.calculate_network_cost(network),
            "Iterations": iterations,
            "Final DP": final_results.get_summary()['total_pressure_drop_Pa'],
            "Target DP": available_dp.to('Pa').value,
        })
        return final_results

    def _get_fluid_properties(self) -> Tuple[float, float]:
        """
        Helper method to get density and viscosity values in base SI units.
        """
        try:
            rho = self._get_density().to('kg/m^3').value
            mu = self._get_viscosity().to('Pa.s').value
            return rho, mu
        except ValueError as e:
            raise ValueError(f"Fluid properties are incomplete or invalid: {e}")


    def _solve_network(self, network: PipelineNetwork, q_in: Optional[Union[VolumetricFlowRate, MassFlowRate]] = None) -> Tuple[Pressure, List[Dict], List[Dict]]:
        """
        Iteratively solves for flow distribution and pressure drops in a network.
        Automatically propagates mass or volumetric flowrates and validates consistency.
        
        Args:
            network: PipelineNetwork instance.
            q_in: Input flowrate (VolumetricFlowRate or MassFlowRate). If mass, converts automatically.
        
        Returns:
            total_system_dp: Pressure object representing total DP across network.
            element_results: List of dicts containing individual element results.
            branch_results: For parallel branches, list of dicts with branch-level results.
        """

        # --- 1. Infer volumetric flow rate ---
        if q_in is None:
            q_in = self.data.get("flowrate") or self._infer_flowrate()
        elif isinstance(q_in, MassFlowRate):
            rho = self._get_density()
            q_in = VolumetricFlowRate(q_in.value / rho.value, "m3/s")

        # --- 2. Initial assignment ---
        for pipe in network.get_all_pipes():
            pipe.current_flow = q_in

        # --- 3. Iterative solver for series/parallel network ---
        max_iterations = 100
        tolerance = 1e-6
        for iteration in range(max_iterations):
            total_dp, element_results, branch_results = self._compute_network(network, q_in)

            # Check convergence: all velocities > 0 and total DP is stable
            max_error = 0
            for el in network.get_all_pipes():
                # Recalculate velocity for validation
                d = self._internal_diameter_m(el)
                el.velocity = FluidVelocity(volumetric_flow_rate=el.current_flow, diameter=d).calculate()
                # Update DP
                el_dp = self._pipe_calculation(el, el.current_flow)["pressure_drop"].value
                max_error = max(max_error, abs(el_dp - getattr(el, "calculated_dp", Pressure(0, "Pa")).value))
                el.calculated_dp = Pressure(el_dp, "Pa")

            if max_error < tolerance:
                break
        else:
            raise RuntimeError(f"Network solver did not converge after {max_iterations} iterations.")

        return total_dp, element_results, branch_results

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
            roughness=get_roughness(pipe.material),
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

    def _compute_network(self, net: PipelineNetwork, q_in: Optional[Union[VolumetricFlowRate, MassFlowRate]] = None) -> Tuple[Pressure, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Recursively computes the pressure drop across a network.
        Automatically handles series and parallel connections and uses volumetric or mass flow rates.
        
        Args:
            net: PipelineNetwork instance representing the network.
            q_in: Optional input flowrate. Can be VolumetricFlowRate or MassFlowRate.
        
        Returns:
            total_pressure_drop: Total pressure drop across this network.
            element_results: List of results for pipes/fittings/equipment.
            branch_results: For parallel networks, list of branch results.
        """

        # --- 1. Infer volumetric flow rate if mass flow is given ---
        if q_in is None:
            q_in = self.data.get("flowrate") or self._infer_flowrate()
        elif isinstance(q_in, MassFlowRate):
            rho = self._get_density()
            q_in = VolumetricFlowRate(q_in.value / rho.value, "m3/s")
        
        # --- 2. Handle series elements ---
        series_list = [el for el in net.elements if getattr(el, "connection_type", "series") == "series"]
        dp_series, results_series = self._compute_series(series_list, q_in, self.data.get("fluid"))

        # --- 3. Handle parallel branches ---
        parallel_branches = [el for el in net.elements if getattr(el, "connection_type", "") == "parallel"]
        branch_results = []
        dp_parallel = Pressure(0, "Pa")

        if parallel_branches:
            # Determine flow for each branch based on flow_split or equal split
            branch_flows = self._resolve_parallel_flows(net, q_in, parallel_branches)
            for idx, branch in enumerate(parallel_branches):
                q_branch = branch_flows[idx]
                q_branch_vol = q_branch if isinstance(q_branch, VolumetricFlowRate) else VolumetricFlowRate(q_branch / self._get_density().value, "m3/s")
                dp_branch, el_results, _ = self._compute_network(branch, q_branch_vol)
                dp_parallel = max(dp_parallel, dp_branch)  # Parallel pressure drop is max across branches
                branch_results.append({
                    "branch_name": getattr(branch, "name", f"branch_{idx}"),
                    "pressure_drop": dp_branch,
                    "elements": el_results,
                    "flow_rate": q_branch_vol
                })

        # Total network DP = series DP + max parallel DP
        total_dp = dp_series + dp_parallel

        # --- 4. Validation: ensure all flow rates and velocities are consistent ---
        for el in net.elements:
            if isinstance(el, Pipe):
                # Recompute velocity from flowrate and diameter
                q_pipe = getattr(el, "current_flow", q_in)
                d_pipe = self._internal_diameter_m(el)
                el.velocity = FluidVelocity(volumetric_flow_rate=q_pipe, diameter=d_pipe).calculate()
                # Validate flowrate
                if el.velocity.value <= 0:
                    raise ValueError(f"Invalid velocity computed for pipe {el.name}. Check diameter/flowrate inputs.")
            elif isinstance(el, PipelineNetwork):
                # Recursive validation inside nested network
                self._compute_network(el, getattr(el, "current_flow", q_in))

        # Aggregate all element results
        all_results = results_series + [b["elements"] for b in branch_results]
        flat_results = [item for sublist in all_results for item in (sublist if isinstance(sublist, list) else [sublist])]

        return total_dp, flat_results, branch_results

    # -------------------- RUN / SUMMARY --------------------------------------

    def run(self) -> PipelineResults:
        """Main execution method: single-pipe or network simulation."""
        network = self.data.get("network")
        pipe = self.data.get("pipe")
        diameter = self.data.get("diameter")
        available_dp = self.data.get("available_dp")
        rho = self._get_density().value
        g = 9.81

        # --- Step 1: Sizing if available DP is provided ---
        if isinstance(network, PipelineNetwork) and available_dp is not None:
            if any(p.nominal_diameter is None for p in network.get_all_pipes()):
                return self._solve_for_diameter(available_dp, **self.data)

        if network is None and pipe is None and diameter is None and available_dp is not None:
            return self._solve_for_diameter(available_dp, **self.data)

        if diameter is not None and pipe is None and network is None:
            self.pipe = self._ensure_pipe()
            self.pipe.internal_diameter = diameter
            print(f"Pipe internal diameter set to: {diameter}")
            velocity = self._maybe_velocity(pipe=self.pipe)
            if velocity is not None:
                self.pipe.velocity = velocity
                print(f"Pipe velocity set to: {velocity}")

        # --- Step 2: Forward simulation ---
        q_in = self._infer_flowrate()

        results: Dict[str, Any] = {}

        # Network mode
        if isinstance(network, PipelineNetwork):
            total_dp, element_results, branch_summaries = self._solve_network(network, q_in)
            total_head = total_dp.value / (rho * g)
            total_power = total_dp.value * q_in.value

            results["mode"] = "network"
            results["summary"] = {
                "inlet_flow": q_in.value,
                "outlet_flow": q_in.value,
                "total_pressure_drop": total_dp,
                "total_head_loss": total_head,
                "total_power_required": total_power,
            }
            results["components"] = element_results
            results["parallel_sections"] = branch_summaries

        # Single-pipe mode
        else:
            pipe_instance = self._ensure_pipe()
            v = self._maybe_velocity(pipe_instance)
            Re = self._reynolds(v, pipe_instance)
            f = self._friction_factor(Re, pipe_instance)

            dp_major = self._major_loss_dp(f, v, pipe_instance)
            dp_minor = Pressure(0.0, "Pa")
            components_list = []

            for ft in self.data.get("fittings", []):
                dp_ft = self._minor_loss_dp(ft, v, f=f, d=self._internal_diameter_m(pipe_instance))
                dp_minor += dp_ft
                components_list.append({
                    "type": "fitting",
                    "name": getattr(ft, "name", getattr(ft, "fitting_type", "unknown")),
                    "pressure_drop": dp_ft,
                })

            total_dp = dp_major + dp_minor
            total_head = total_dp.value / (rho * g)
            total_power = total_dp.value * q_in.value

            results["mode"] = "single_pipe"
            results["summary"] = {
                "flowrate": q_in.value,
                "total_pressure_drop": total_dp,
                "total_head_loss": total_head,
                "total_power_required": total_power,
            }
            results["components"] = [{
                "type": "pipe",
                "name": pipe_instance.name,
                "length": pipe_instance.length,
                "diameter": self._internal_diameter_m(pipe_instance),
                "velocity": v,
                "reynolds": Re,
                "friction_factor": f,
                "major_dp": dp_major,
                "minor_dp": dp_minor,
                "total_dp": total_dp,
            }] + components_list

        self._results = PipelineResults(results)
        return self._results