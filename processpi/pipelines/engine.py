# processpi/pipelines/engine.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import math

# Local package imports (assumed to exist in your project)
from ..units import (
    Diameter, Length, Pressure, Density, Viscosity, VolumetricFlowRate, Velocity, MassFlowRate, Variable, Dimensionless
)
from .pipelineresults import PipelineResults
from .nozzle import Nozzle
from ..components import Component
from .standards import (
    get_k_factor, get_roughness, list_available_pipe_diameters, get_standard_pipe_data,
    get_recommended_velocity, get_next_standard_nominal, get_next_next_standard_nominal, get_previous_standard_nominal,get_equivalent_length,get_internal_diameter,get_nominal_dia_from_internal_dia
)
from .pipes import Pipe
from .fittings import Fitting
from .equipment import Equipment
from .network import PipelineNetwork
from .piping_costs import PipeCostModel
from ..calculations.fluids import (
    FluidVelocity, ReynoldsNumber, PressureDropDarcy, OptimumPipeDiameter, PressureDropFanning, ColebrookWhite, PressureDropHazenWilliams
)
from processpi.pipelines import network


# ------------------------------- Constants ---------------------------------
G = 9.80665  # m/s^2, Standard gravity
DEFAULT_PUMP_EFFICIENCY = 0.70
DEFAULT_FLOW_TOL = 1e-6  # m3/s, Absolute flow tolerance for solvers
MAX_HC_ITER = 200  # Max iterations for Hardy-Cross solver
MAX_MATRIX_ITER = 100 # Max iterations for matrix solver

# ------------------------------- Helpers -----------------------------------


def _to_m3s(maybe_flow: Any) -> VolumetricFlowRate:
    """
    Normalize flow to VolumetricFlowRate (m^3/s).

    Args:
        maybe_flow (Any): The flow rate, which can be a VolumetricFlowRate object,
                          a MassFlowRate object, or a number.

    Returns:
        VolumetricFlowRate: The flow rate in m^3/s.

    Raises:
        ValueError: If flow is None.
        TypeError: If a MassFlowRate object is provided without density context.
    """
    if maybe_flow is None:
        raise ValueError("Flow cannot be None")
    if isinstance(maybe_flow, VolumetricFlowRate):
        return maybe_flow
    if isinstance(maybe_flow, MassFlowRate):
        raise TypeError("MassFlowRate provided without density context. Convert before calling.")
    # assume numeric m3/s
    return VolumetricFlowRate(float(maybe_flow), "m3/s")


def _ensure_diameter_obj(d: Any, assume_mm: bool = True) -> Diameter:
    """
    Ensures the input is a Diameter object.

    If the input `d` is not a Diameter object, it attempts to convert it to one.
    The `assume_mm` flag determines if a raw number is treated as millimeters.

    Args:
        d (Any): The diameter value or object.
        assume_mm (bool): If True, a numeric input is assumed to be in millimeters.

    Returns:
        Diameter: The validated or converted Diameter object.
    """
    if isinstance(d, Diameter):
        return d
    val = float(d)
    unit = "mm" if assume_mm else "m"
    return Diameter(val, unit)


@dataclass
class ElementReport:
    """
    A data class to store the results of a single pipeline element calculation.
    """
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
        """Convert the dataclass to a dictionary."""
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
    """
    Pipeline simulation and sizing engine.

    This class provides a comprehensive set of tools for modeling fluid flow
    in pipelines. It can handle single pipes, series networks, and parallel
    networks, calculating pressure drop, velocity, Reynolds number, and other
    key fluid properties.

    Usage:
        1. Instantiate the engine: `engine = PipelineEngine()`
        2. Configure inputs with `.fit()`: `engine.fit(fluid=water, flowrate=1.0)`
        3. Run the simulation: `results = engine.run()`
        4. Access results: `results.summary()`

    The object stores the last results in `self._results` (PipelineResults).
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the PipelineEngine.

        Args:
            **kwargs: Initial configuration parameters passed to `fit()`.
        """
        self.data: Dict[str, Any] = {}
        self._results: Optional[PipelineResults] = None
        if kwargs:
            self.fit(**kwargs)

    # ---------------------- Configuration / Fit ----------------------------
    def fit(self, **kwargs: Any) -> "PipelineEngine":
        """
        Configures engine inputs with unit-aware conversions and normalized keys.

        Args:
            **kwargs: Input parameters (e.g., flowrate, diameter, network).

        Returns:
            PipelineEngine: The configured engine instance.

        Raises:
            TypeError: If the provided network is not a PipelineNetwork.
        """
        self.data = dict(kwargs)

        # Map aliases to canonical keys
        alias_map = {
            "flowrate": ["flow_rate", "q", "Q", "flowrate"],
            "mass_flowrate": ["mass_flow", "m_dot", "mdot"],
            "velocity": ["v"],
            "diameter": ["dia", "D", "nominal_diameter", "internal_diameter"],
            "length": ["len", "L"],
            "inlet_pressure": ["in_pressure", "pin", "p_in"],
            "outlet_pressure": ["out_pressure", "pout", "p_out"],
        }

        for canonical, aliases in alias_map.items():
            if canonical not in self.data:
                for a in aliases:
                    if a in self.data:
                        self.data[canonical] = self.data[a]
                        break

        # Default values
        self.data.setdefault("assume_mm_for_numbers", True)
        self.data.setdefault("flow_split", {})
        self.data.setdefault("tolerance_m3s", DEFAULT_FLOW_TOL)
        self.data.setdefault("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
        self.data.setdefault("method", "darcy_weisbach")
        self.data.setdefault("hw_coefficient", 130.0)
        self.data.setdefault("solver", "auto")

        # Validate network
        net = self.data.get("network")
        if net is not None and not isinstance(net, PipelineNetwork):
            raise TypeError("`network` must be a PipelineNetwork instance.")

        # Bind normalized attributes
        self.flowrate = self.data.get("flowrate")
        self.mass_flowrate = self.data.get("mass_flowrate")
        self.velocity = self.data.get("velocity")
        self.diameter = self.data.get("diameter")

        return self


    # ---------------------- Fluid properties --------------------------------
    def _get_density(self) -> Density:
        """
        Retrieves the fluid's density.

        Returns:
            Density: The fluid density object.

        Raises:
            ValueError: If density is not provided or cannot be inferred from the fluid component.
        """
        if "density" in self.data and self.data["density"] is not None:
            return self.data["density"]
        fluid = self.data.get("fluid")
        if isinstance(fluid, Component):
            return fluid.density()
        raise ValueError("Provide 'density' or a 'fluid' Component with density().")

    def _get_viscosity(self) -> Viscosity:
        """
        Retrieves the fluid's dynamic viscosity.

        Returns:
            Viscosity: The fluid viscosity object.

        Raises:
            ValueError: If viscosity is not provided or cannot be inferred from the fluid component.
        """
        if "viscosity" in self.data and self.data["viscosity"] is not None:
            return self.data["viscosity"]
        fluid = self.data.get("fluid")
        if isinstance(fluid, Component):
            return fluid.viscosity()
        raise ValueError("Provide 'viscosity' or a 'fluid' Component with viscosity().")

    # ---------------------- Flow inference ----------------------------------
    def _infer_flowrate(self) -> VolumetricFlowRate:
        """
        Infers the volumetric flow rate from available data.

        Priority:
        1. Volumetric flow provided directly.
        2. Mass flow provided → convert using density.
        3. Velocity + diameter → calculate volumetric flow.

        Returns:
            VolumetricFlowRate: The calculated volumetric flow rate.

        Raises:
            ValueError: If flow rate cannot be inferred.
        """
        # 1️⃣ Use volumetric flow if provided
        if "flowrate" in self.data and self.data["flowrate"] is not None:
            fr = self.data["flowrate"]
            if not isinstance(fr, VolumetricFlowRate):
                fr = VolumetricFlowRate(float(fr), "m3/s")
            self.data["flowrate"] = fr
            return fr

        # 2️⃣ Convert mass flow to volumetric flow
        if "mass_flowrate" in self.data and self.data["mass_flowrate"] is not None:
            m: MassFlowRate = self.data["mass_flowrate"]
            rho: Density = self._get_density()

            # Convert mass flow to kg/s and density to kg/m3
            m_kg_s = m.to("kg/s").value
            rho_kg_m3 = rho.to("kg/m3").value

            q_val = m_kg_s / rho_kg_m3
            q = VolumetricFlowRate(q_val, "m3/s")
            self.data["flowrate"] = q
            return q

        # 3️⃣ Compute from velocity + diameter
        v = self.data.get("velocity")
        d = self.data.get("diameter")
        if v is not None and d is not None:
            if not isinstance(v, Velocity):
                v = Velocity(float(v), "m/s")
            d_obj = _ensure_diameter_obj(d, self.data.get("assume_mm_for_numbers", True))
            area_m2 = math.pi * (d_obj.to("m").value ** 2) / 4.0
            q = VolumetricFlowRate(v.to("m/s").value * area_m2, "m3/s")
            self.data["flowrate"] = q
            return q

        # If none of the above, raise an error
        raise ValueError(
            "Unable to infer flowrate. Provide 'flowrate', 'mass_flowrate', "
            "or both 'velocity' and 'diameter'."
        )

    
    def _maybe_velocity(self, pipe):
        """
        Ensures velocity is available.

        If not explicitly provided, it calculates velocity using volumetric flow
        rate and pipe diameter.

        Args:
            pipe (Pipe): The pipe object to check for velocity.

        Returns:
            Velocity: The velocity object.

        Raises:
            ValueError: If velocity cannot be calculated.
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
        """
        Resolves the internal diameter for a given pipe or the simulation.

        Priority order:
        1. `pipe.internal_diameter`
        2. `pipe.nominal_diameter`
        3. `engine.diameter` from `self.data`
        4. Calculates the optimum diameter as a fallback.

        Args:
            pipe (Optional[Pipe]): The pipe object for which to resolve the diameter.

        Returns:
            Diameter: The resolved internal diameter.
        """
        if pipe is not None:
            if getattr(pipe, "internal_diameter", None) is not None:
                d = pipe.internal_diameter
                return d if isinstance(d, Diameter) else Diameter(float(d), "m")
            if getattr(pipe, "nominal_diameter", None) is not None:
                d = pipe.nominal_diameter
                return d if isinstance(d, Diameter) else Diameter(float(d), "m")
        d = self.data.get("diameter")
        if d is not None:
            # print(d) # For debugging
            return d if isinstance(d, Diameter) else _ensure_diameter_obj(d, self.data.get("assume_mm_for_numbers", True))
        # fallback to compute optimum for a single pipe
        q = self._infer_flowrate()
        calc = OptimumPipeDiameter(flow_rate=q, density=self._get_density())
        return calc.calculate()

    # ---------------------- Primitive calculators ---------------------------
    def _velocity(self, q: VolumetricFlowRate, d: Diameter) -> Velocity:
        """
        Calculates the fluid velocity given flow rate and diameter.
        """
        return FluidVelocity(volumetric_flow_rate=q, diameter=d).calculate()

    def _reynolds(self, v: Velocity, d: Diameter) -> float:
        """
        Calculates the Reynolds number.
        """
        return ReynoldsNumber(density=self._get_density(), velocity=v, diameter=d, viscosity=self._get_viscosity()).calculate()

    def _friction_factor(self, Re: float, d: Diameter, material: Optional[str] = None) -> float:
        """
        Calculates the friction factor using the Colebrook-White equation.
        """
        #print(material)
        eps = get_roughness(material) if material else 0.0
        #print(eps)
        # print(Re) # For debugging
        return ColebrookWhite(reynolds_number=Re, roughness=eps, diameter=d).calculate()

    def _major_dp_pa(self, f: float, L: Length, d: Diameter, v: Velocity) -> Pressure:
        """
        Calculates the major pressure drop (friction loss) using the Darcy-Weisbach equation.
        """
        #print("Length:", L)
        return PressureDropDarcy(
            friction_factor=f,
            length=L,
            diameter=d,
            density=self._get_density(),
            velocity=v
        ).calculate()

    def _minor_dp_pa(self, fitting: Fitting, v: Velocity, f: Optional[float], d: Diameter) -> Pressure:
        """
        Calculates the minor pressure drop (fitting loss).

        It prioritizes the K-factor method and falls back to the equivalent length method,
        then to standards lookup.
        """
        rho = self._get_density().value
        v_val = v.value if hasattr(v, "value") else float(v)

        # 1. Try explicit K-factor first
        K = getattr(fitting, "K", None) or getattr(fitting, "K_factor", None) or getattr(fitting, "total_K", None)
        #print(K)
        if K is not None:
            return Pressure(0.5 * rho * v_val * v_val * float(K), "Pa")
        
        # 2. Try explicit equivalent length on the fitting
        Le_candidate = getattr(fitting, "Le", None) or getattr(fitting, "equivalent_length", None) or getattr(fitting, "total_Le", None)
        #print(Le_candidate)
        # Perform the Le/D calculation if an equivalent length value was found
        if Le_candidate is not None:
            le_val = None
            if isinstance(Le_candidate, Length):
                #print("Le is Length")
                le_val = Le_candidate.to("m").value
            elif callable(Le_candidate):
                # Check if the method call returns a value before using it
                le_result = Le_candidate()
                #print(le_result)
                if le_result is not None:
                    le_val = le_result * d.to("m").value
                #print(le_val)
            else:
                # Assumes Le is a numerical value representing the Le/D ratio.
                le_val = float(Le_candidate) * d.to("m").value
                
            
            # If a valid equivalent length value was found, perform the calculation
            if le_val is not None:
                if f is None:
                    Re = self._reynolds(v, d)
                    friction_factor_obj = self._friction_factor(Re, d)
                    f_val = friction_factor_obj.value
                else:
                    f_val = float(f.value) if isinstance(f, Variable) else float(f)
                #print("Le value:", le_val)
                return Length(le_val, "m")

        # 3. Fallback to standards lookup (for K-factor) if no explicit Le/D was found
        fitting_type = getattr(fitting, "fitting_type", None)
        if fitting_type is not None:
            Re = self._reynolds(v, d)
            pipe = self.data.get("pipe")
            roughness = get_roughness(getattr(pipe, "material", None))
            
            K_from_standards = get_k_factor(fitting_type, Re, roughness, d.value)
            #print(K_from_standards)
            if K_from_standards is not None:
                return Pressure(0.5 * rho * v_val * v_val * float(K_from_standards), "Pa")
            else:
                print(f"Warning: No standard K-factor or equivalent length found for fitting type '{fitting_type}'")

        return Pressure(0.0, "Pa")
    # ---------------------- Pipe calculation (major+minor+elevation) ---------
    def _pipe_calculation(self, pipe: Pipe, flow_rate: Optional[VolumetricFlowRate]) -> Dict[str, Any]:
        """
        Calculates velocity, Reynolds number, friction factor, and pressure drops
        for a single pipe including minor losses from all fittings.
        """
        # ---------------------------
        # Diameter
        # ---------------------------
        d = pipe.internal_diameter or self._resolve_internal_diameter(pipe)
        if d is None or getattr(d, "value", d) <= 0:
            d = Diameter(0.01, "m")  # fallback

        # ---------------------------
        # Flow Rate & Velocity
        # ---------------------------
        q_used = flow_rate or getattr(pipe, "assigned_flow_rate", None) or self._infer_flowrate()
        if q_used is None or getattr(q_used, "value", q_used) <= 0:
            q_used = VolumetricFlowRate(1e-12, "m3/s")  # avoid division by zero

        v = getattr(pipe, "velocity", None) or Velocity(FluidVelocity(volumetric_flow_rate=q_used, diameter=d).calculate().value, "m/s")
        
        # ---------------------------
        # Reynolds Number & Friction
        # ---------------------------
        #print(d)
        Re = self._reynolds(v, d)
        material = getattr(pipe, "material", None)
        method = self.data.get("method", "darcy_weisbach").lower()

        if getattr(Re, "value", Re) <= 1e-8:
            f = 0.0
            dp_major = self._major_dp_pa(f, pipe.length or Length(1.0, "m"), d, v)
        elif method == "hazen_williams":
            hw_coeff = getattr(pipe, "hw_coefficient", None) or self.data.get("hw_coefficient", 130.0)
            dp_major = PressureDropHazenWilliams({
                "length": pipe.length or Length(1.0, "m"),
                "flow_rate": q_used,
                "coefficient": hw_coeff,
                "diameter": d,
                "density": self._get_density(),
            }).calculate()
            f = None
        else:
            #print(f"   Testing Diameter: {d.to('in')} ({d.value:.3f} m) → Pressure Drop: {dp_major.value:.2f} Pa")
            f = self._friction_factor(Re, d, material=pipe.material)
            #print(f"  Reynolds Number: {Re:.2e}, Friction Factor: {f:.4f} pipe length: {pipe.length}, diameter: {d.to('in')} ({d.value:.3f} m), velocity: {v:.2f} m/s")
            dp_major = self._major_dp_pa(f, pipe.length or Length(1.0, "m"), d, v)
            #print(f"   Testing Diameter: {d.to('in')} ({d.value:.3f} m) → Pressure Drop: {dp_major.value:.2f} Pa")
        # ---------------------------
        # Minor Losses (always included)
        # ---------------------------
        #print(f"   Major Losses: {dp_major.to('Pa').value:.2f} Pa")
        dp_minor = Pressure(0.0, "Pa")
        ft = getattr(pipe, "fittings", []) or [] or getattr(self.data.get("pipe"), "fittings", []) or [] or getattr(self.data.get("fittings"), "fittings", []) or []
        #ft.diameter = 
        for ft in ft:
            ft.diameter = d
            le_val = self._minor_dp_pa(ft, v, f, d)
            #print(le_val)
            equivalent_length = Length(0.0, "m")
            if isinstance(le_val, Length):
                #print(le_val,d.value,ft.quantity)
                equivalent_length = le_val.value * ft.quantity
                #print(equivalent_length)
                dp_minor += self._major_dp_pa(f, equivalent_length, d, v)
                #print(dp_minor)
            elif isinstance(le_val, Pressure):
                dp_minor += le_val
            else:
                # If neither Length nor Pressure, skip or handle as needed
                pass
        #print(f"   Minor Losses: {dp_minor.to('Pa').value:.2f} Pa")
        # ---------------------------
        # Elevation Loss
        # ---------------------------
        rho_val = self._get_density().value
        start_node = getattr(pipe, "start_node", None)
        end_node = getattr(pipe, "end_node", None)
        elev_loss = Pressure(0.0, "Pa")
        try:
            elev_diff_m = float(getattr(end_node, "elevation", 0.0)) - float(getattr(start_node, "elevation", 0.0))
            elev_loss = Pressure(rho_val * 9.80665 * elev_diff_m, "Pa")
        except Exception:
            pass

        # ---------------------------
        # Total Pressure Drop
        # ---------------------------
        total_dp_pa = sum(getattr(x, "value", x) for x in [dp_major, dp_minor, elev_loss])
        #print(total_dp_pa,dp_major,dp_minor,elev_loss)
        #print(f"   Total Pressure Drop: {total_dp_pa:.2f} Pa")
        return {
            "diameter": d,
            "velocity": v,
            "reynolds": Re,
            "friction_factor": f,
            "major_dp": dp_major,
            "minor_dp": dp_minor,
            "elevation_dp": elev_loss,
            "pressure_drop": Pressure(total_dp_pa, "Pa"),
            "major_dp_pa": getattr(dp_major, "value", dp_major),
            "minor_dp_pa": getattr(dp_minor, "value", dp_minor),
            "elevation_dp_pa": getattr(elev_loss, "value", elev_loss),
        }


    # ---------------------- Series/Parallel evaluation -------------------------

    def _compute_series(self, series: Any, flow_rate: Optional[VolumetricFlowRate] = None) -> Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Compute pressure drop for a series of pipes.

        Args:
            series (Any): A single Pipe, a list of Pipes (treated as series),
                          or a list of branches (each branch is a list of Pipes).
            flow_rate (Optional[VolumetricFlowRate]): The flow rate for the series.

        Returns:
            Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
                - total pressure drop
                - list of element reports
                - series summary dictionary
        """

        # ---------------------------
        # Normalize input
        # ---------------------------
        if isinstance(series, Pipe):
            # Single pipe -> one series with one pipe
            series = [series]
        elif all(isinstance(p, Pipe) for p in series):
            # Already a list of pipes -> fine
            pass
        elif all(isinstance(b, list) for b in series):
            # List of branches -> flatten for series calculation
            series = [p for branch in series for p in branch]
            if not all(isinstance(p, Pipe) for p in series):
                raise TypeError("After flattening, series contains non-Pipe elements")
        else:
            raise TypeError("series must be a Pipe, list of Pipes, or list of branches (list of Pipes)")

        # ---------------------------
        # Series flow calculation
        # ---------------------------
        total_dp = 0.0
        element_reports = []

        for idx, pipe in enumerate(series):
            pipe_res = self._pipe_calculation(pipe, flow_rate)
            dp_val = getattr(pipe_res["pressure_drop"], "value", pipe_res["pressure_drop"])
            total_dp += dp_val

            element_reports.append({
                "name": getattr(pipe, "name", f"Pipe_{idx}"),
                "type": "pipe",
                **pipe_res
            })

        # ---------------------------
        # Series summary
        # ---------------------------
        series_summary = {
            "total_pressure_drop": Pressure(total_dp, "Pa"),
            "number_of_elements": len(series),
            "average_velocity": Velocity(
                sum(getattr(el["velocity"], "value", el["velocity"]) for el in element_reports) / len(element_reports),
                "m/s"
            ),
            "elements": element_reports
        }

        return Pressure(total_dp, "Pa"), element_reports, series_summary


    def _compute_network(
        self,
        network: Any,
        flow_rate: Optional[VolumetricFlowRate] = None
    ) -> Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Compute total pressure drop for a network, including major, minor, and elevation losses.

        Args:
            network (Any): Pipe, list of Pipes (series branch), list of branches (each branch is list of Pipes),
                        or a PipelineNetwork object.
            flow_rate (Optional[VolumetricFlowRate]): The flow rate for the network.

        Returns:
            Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
                - total network pressure drop
                - element reports (major + minor + elevation)
                - network summary
        """

        # ---------------------------
        # Normalize input to branches
        # ---------------------------
        if isinstance(network, Pipe):
            branches = [[network]]
        elif isinstance(network, list):
            # series branch or multiple branches
            if all(isinstance(p, Pipe) for p in network):
                branches = [network]
            elif all(isinstance(b, list) for b in network):
                branches = []
                for b in network:
                    if all(isinstance(p, Pipe) for p in b):
                        branches.append(b)
                    else:
                        raise TypeError("Each branch must be a list of Pipe objects")
            else:
                raise TypeError("Network list must contain Pipes or branches (lists of Pipes)")
        elif hasattr(network, "branches") and isinstance(network.branches, list):
            branches = []
            for b in network.branches:
                if isinstance(b, Pipe):
                    branches.append([b])
                elif isinstance(b, list) and all(isinstance(p, Pipe) for p in b):
                    branches.append(b)
                else:
                    raise TypeError("PipelineNetwork branches must contain Pipes or lists of Pipes")
        else:
            raise TypeError("Network must be Pipe, list of Pipes/branches, or PipelineNetwork object")

        # ---------------------------
        # Compute network
        # ---------------------------
        total_network_dp = 0.0
        all_element_reports: List[Dict[str, Any]] = []

        for branch_idx, branch in enumerate(branches):
            branch_dp = 0.0
            branch_element_reports = []

            for pipe in branch:
                # compute all losses for this pipe
                calc = self._pipe_calculation(pipe, flow_rate)

                dp_value = getattr(calc["pressure_drop"], "value", calc["pressure_drop"])
                branch_dp += dp_value

                # build element-level report
                report = {
                    "name": getattr(pipe, "name", f"Pipe_{id(pipe)}"),
                    "diameter": calc["diameter"],
                    "velocity": calc["velocity"],
                    "reynolds": calc["reynolds"],
                    "friction_factor": calc["friction_factor"],
                    "major_dp": calc["major_dp"],
                    "minor_dp": calc["minor_dp"],
                    "elevation_dp": calc["elevation_dp"],
                    "total_dp": calc["pressure_drop"],
                }

                branch_element_reports.append(report)

            # tag branch index
            for el in branch_element_reports:
                el["branch_index"] = branch_idx

            all_element_reports.extend(branch_element_reports)
            total_network_dp += branch_dp

        # ---------------------------
        # Network summary
        # ---------------------------
        network_summary = {
            "total_pressure_drop": Pressure(total_network_dp, "Pa"),
            "number_of_branches": len(branches),
            "number_of_elements": len(all_element_reports),
            "elements": all_element_reports
        }

        return Pressure(total_network_dp, "Pa"), all_element_reports, network_summary


    def _resolve_parallel_flows(
        self, net: PipelineNetwork, q_total: VolumetricFlowRate, branches: list, tol: float = 1e-3, max_iter: int = 100
    ) -> list:
        """
        Resolves flow in parallel branches using iterative ΔP balancing.
        
        Args:
            net (PipelineNetwork): The parallel network object.
            q_total (VolumetricFlowRate): Total volumetric flow rate (m3/s).
            branches (list): List of branch networks.
            tol (float): Convergence tolerance on ΔP equality.
            max_iter (int): Maximum iterations.
        
        Returns:
            List[float]: A list of flow rates (m3/s) for each branch.
        """
        n = len(branches)
        # --- Initial guess: equal split ---
        q_branches = [q_total.value / n] * n

        # Check for user-defined split ratios
        split_cfg = (self.data.get("flow_split") or {}).get(net.name)
        if split_cfg:
            vals = [float(x) for x in split_cfg]
            if sum(vals) > 1.5 * q_total.value:  # absolute flows
                return vals
            s = sum(vals)  # ratios
            return [q_total.value * (v / s) for v in vals]

        # --- Iterative ΔP balancing ---
        for iteration in range(max_iter):
            dps = []
            for i, branch in enumerate(branches):
                flow_i = VolumetricFlowRate(q_branches[i], "m3/s")
                dp, _, _ = self._compute_network(branch, flow_i)
                dps.append(dp.to("Pa").value)

            dp_avg = sum(dps) / n
            # Convergence: all ΔPs within tolerance
            if max(abs(dp - dp_avg) for dp in dps) / (dp_avg + 1e-6) < tol:
                break

            # Adjust flows proportionally: higher ΔP → reduce flow, lower ΔP → increase flow
            for i in range(n):
                if dps[i] == 0:  # avoid division by zero
                    continue
                factor = dp_avg / dps[i]
                q_branches[i] *= factor
            # Normalize total flow
            q_sum = sum(q_branches)
            q_branches = [q * q_total.value / q_sum for q in q_branches]

        return q_branches





    # ---------------------- Network Solvers ---------------------------------
    def _hardy_cross(self, network: PipelineNetwork, q_total: VolumetricFlowRate, tol: float) -> Tuple[bool, float, List[ElementReport]]:
        """
        Hardy-Cross iterative solver for a parallel/looped network.

        Args:
            network (PipelineNetwork): The network object to solve.
            q_total (VolumetricFlowRate): The total flow rate entering the network.
            tol (float): The convergence tolerance.

        Returns:
            Tuple[bool, float, List[ElementReport]]:
                - bool: True if the solver converged.
                - float: The final maximum residual.
                - List[ElementReport]: A list of element reports with calculated properties.
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
                # derivative estimate dH/dQ ≈ n * H / Q (heuristic better than 2*H/Q in mixed networks)
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

    def _matrix_solver(self, network: Any, q_total: VolumetricFlowRate, tol: float = 1e-6
                  ) -> Tuple[bool, List[VolumetricFlowRate], List[Dict[str, Any]]]:
        """
        Solve the network using an iterative approach.

        Args:
            network (Any): The network to solve.
            q_total (VolumetricFlowRate): Total volumetric flow rate.
            tol (float): Convergence tolerance.

        Returns:
            Tuple[bool, List[VolumetricFlowRate], List[Dict[str, Any]]]:
                - matrix_ok: bool indicating convergence
                - matrix_res: list of branch flow rates
                - matrix_reports: detailed element reports
        """

        # Normalize network using _compute_network
        _, element_reports, network_summary = self._compute_network(network, q_total)
        n_branches = network_summary["number_of_branches"]

        # Initialize branch flows equally if not set
        branch_flows = [q_total / n_branches for _ in range(n_branches)]
        matrix_ok = False
        iteration = 0
        max_iter = 100

        while iteration < max_iter:
            iteration += 1
            # dp_prev = [self._compute_network(branch, q)[0].value for branch, q in zip(self._normalize_branches(network), branch_flows)]

            # Recompute pressure drops for each branch with current flows
            dp_new = []
            for idx, branch in enumerate(self._normalize_branches(network)):
                dp, _, _ = self._compute_network(branch, branch_flows[idx])
                dp_new.append(getattr(dp, "value", dp))

            # Compute flow correction
            corrections = [dp / max(dp_new) * branch_flows[idx] for idx, dp in enumerate(dp_new)]
            max_change = max(abs(c - f.value if hasattr(f, "value") else f - bf) for c, bf in zip(corrections, branch_flows))
            branch_flows = corrections

            if max_change < tol:
                matrix_ok = True
                break

        matrix_reports = []
        for branch_idx, branch in enumerate(self._normalize_branches(network)):
            _, el_reports, _ = self._compute_network(branch, branch_flows[branch_idx])
            for el in el_reports:
                el["branch_index"] = branch_idx
            matrix_reports.extend(el_reports)

        return matrix_ok, branch_flows, matrix_reports


    def _solve_network_dual(self, network: Any, q_total: VolumetricFlowRate, tol: float = 1e-6) -> Tuple[Dict[str, Any], Any]:
        """
        Top-level solver for networks with multiple branches.

        Iteratively balances flows across parallel branches,
        ensuring all minor losses are included.
        """
        branches = self._normalize_branches(network)
        n_branches = len(branches)
        branch_flows = [q_total.value / n_branches for _ in range(n_branches)]
        max_iter = 50
        converged = False

        for iteration in range(max_iter):
            dp_values = []
            for idx, branch in enumerate(branches):
                dp, _, _ = self._compute_network(branch, branch_flows[idx])
                dp_values.append(getattr(dp, "value", dp))

            dp_mean = sum(dp_values) / len(dp_values)
            corrections = [bf * dp_mean / max(dpv, 1e-12) for bf, dpv in zip(branch_flows, dp_values)]
            max_change = max(abs(c - bf) for c, bf in zip(corrections, branch_flows))
            branch_flows = corrections

            if max_change < tol:
                converged = True
                break

        # Generate final component-level reports including minor losses
        final_reports = []
        for idx, branch in enumerate(branches):
            _, el_reports, _ = self._compute_network(branch, branch_flows[idx])
            for el in el_reports:
                el["branch_index"] = idx
                # Ensure minor losses are included for each element
                if "minor_dp" not in el:
                    el["minor_dp"] = getattr(el.get("pressure_drop", 0), "value", 0) - getattr(el.get("major_dp", 0), "value", 0)
            final_reports.extend(el_reports)

        return {
            "success": converged,
            "branch_flows": branch_flows,
            "reports": final_reports,
            "iterations": iteration + 1,
        }, None

    def _normalize_branches(self, network) -> list[list[Pipe]]:
        """
        Converts any PipelineNetwork or list of branches into a flat list of
        branches, where each branch is a list of Pipe objects.

        Args:
            network (Any): The network or list of pipes to normalize.

        Returns:
            list[list[Pipe]]: A flattened list of branches.
        """
        if isinstance(network, Pipe):
            return [[network]]
        elif isinstance(network, list):
            # Flatten each branch recursively
            normalized = []
            for item in network:
                normalized.extend(self._normalize_branches(item))
            return normalized
        elif isinstance(network, PipelineNetwork):
            branches = []
            if network.connection_type == "series":
                # Treat entire series network as a single branch
                series_branch = []
                for el in network.elements:
                    if isinstance(el, Pipe):
                        series_branch.append(el)
                    elif isinstance(el, PipelineNetwork):
                        # Flatten nested series inside this branch
                        nested_branches = self._normalize_branches(el)
                        # For series, nested branch is appended to current branch
                        if nested_branches:
                            series_branch.extend(nested_branches[0])
                branches.append(series_branch)
            elif network.connection_type == "parallel":
                # Each element is a separate branch
                for el in network.elements:
                    if isinstance(el, Pipe):
                        branches.append([el])
                    elif isinstance(el, PipelineNetwork):
                        nested = self._normalize_branches(el)
                        branches.extend(nested)
            return branches
        else:
            raise TypeError("Network must be Pipe, list of Pipes/branches, or PipelineNetwork-like object")




    # ---------------------- Diameter selection -------------------------------
    def _select_standard_diameter(self, ideal_d_m: float) -> Tuple[str, float]:
        """
        Maps a continuous ideal diameter (m) to nearest standard nominal.
        Picks the smallest standard size that yields diameter >= ideal.
        
        Args:
            ideal_d_m (float): The ideal diameter in meters.

        Returns:
            Tuple[str, float]: A tuple of the label and the value in meters.
        """
        standard_list = list_available_pipe_diameters()
        if not standard_list:
            raise ValueError("No standard pipe diameters available.")

        # Ensure numeric values
        standard_list_m = [d.to("m").value if isinstance(d, Diameter) else float(d) for d in standard_list]
        nearest = min(standard_list_m, key=lambda x: abs(x - ideal_d_m))
        label = f"{nearest*1000:.0f} mm"
        return label, nearest

    # ---------------------- Utility helpers ---------------------------------
    def _as_pressure(self, maybe_pressure: Any, default_unit: str = "Pa") -> Optional[Pressure]:
        """
        Converts input to a Pressure object.
        """
        if maybe_pressure is None:
            return None
        if isinstance(maybe_pressure, Pressure):
            return maybe_pressure
        return Pressure(float(maybe_pressure), default_unit)

    def _pump_gain_pa(self, pump: Any) -> Pressure:
        """
        Converts pump object head/pressure to Pa.
        Accepts `head` (m) or inlet/outlet pressures.
        """
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
        """
        Converts Equipment pressure_drop (assumed bar) to Pa if needed.
        """
        dp = getattr(eq, "pressure_drop", 0.0) or 0.0
        return Pressure(float(dp), "bar").to("Pa") if not isinstance(dp, Pressure) else dp

    def _fitting_dp_pa(self, fitting: Fitting, v: Velocity, f: Optional[float], d: Diameter) -> Pressure:
        """
        Compute fitting pressure drop using K or Le approaches.
        """
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
        """Execute pipeline simulation and return PipelineResults with all losses included."""

        # -----------------------
        # Gather inputs
        # -----------------------
        net = self.data.get("network")
        q_in = self._infer_flowrate()  # volumetric flow
        tol = self.data.get("tolerance_m3s", DEFAULT_FLOW_TOL)
        diameter = self.data.get("diameter")
        available_dp = self.data.get("available_dp")
        fluid = self.data.get("fluid")
        G = 9.80665  # gravity for head calculation

        results_out: Dict[str, Any] = {"mode": None, "summary": {}, "components": []}

        # Helper: safely convert unit objects to float values
        def _to_value(obj, prefer_unit: Optional[str] = None):
            if obj is None:
                return 0.0
            try:
                if hasattr(obj, "to") and prefer_unit is not None:
                    conv = obj.to(prefer_unit)
                    return float(getattr(conv, "value", conv))
                if hasattr(obj, "value"):
                    return float(obj.value)
                if hasattr(obj, "magnitude"):
                    return float(obj.magnitude)
                return float(obj)
            except Exception:
                return 0.0

        # -----------------------
        # NETWORK MODE
        # -----------------------
        if isinstance(net, PipelineNetwork):
            # --------------------------------------------------
            # Step 1: Detect pipes missing diameter definitions
            # --------------------------------------------------
            missing_diameter = any(
                getattr(p, "internal_diameter", None) is None and getattr(p, "nominal_diameter", None) is None
                for p in net.get_all_pipes()
            )

            # --------------------------------------------------
            # Step 2: Auto-size missing diameters if any found
            # --------------------------------------------------
            if missing_diameter:
                print("🔄 Auto-sizing network pipe diameters...")
                kwargs = self.data.copy()
                kwargs.pop("network", None)
                sizing_results = self._solve_for_diameter_network(net, **kwargs)

                # Access results directly
                sizing_data = sizing_results.results

                # Apply calculated diameters to network pipes
                for comp in sizing_data.get("all_simulation_results", []):
                    for pipe in net.get_all_pipes():
                        if pipe.name == comp.get("network_name"):
                            pipe.internal_diameter = comp["components"][0]["diameter"]

            # --------------------------------------------------
            # Step 3: Assign flowrate to pipes if missing
            # --------------------------------------------------
            for p in net.get_all_pipes():
                current_flow = getattr(p, "flow_rate", None)
                if current_flow is None or _to_value(current_flow) <= 0:
                    try:
                        p.flow_rate = VolumetricFlowRate(q_in.value, "m3/s")
                    except Exception:
                        p.flow_rate = q_in

            # --------------------------------------------------
            # Step 4: Solve the (now ready) network
            # --------------------------------------------------
            solved_dict, solver_meta = self._solve_network_dual(net, q_in, tol)
            reports = solved_dict.get("reports", []) or []

            # Convert reports to dictionaries
            comp_list = []
            for r in reports:
                if isinstance(r, dict):
                    comp_list.append(r)
                else:
                    try:
                        comp_list.append(r.as_dict())
                    except Exception:
                        comp_list.append({
                            "name": getattr(r, "name", None),
                            "pressure_drop_Pa": _to_value(getattr(r, "pressure_drop_Pa", None)),
                            "minor_dp": _to_value(getattr(r, "minor_dp", 0.0)),
                            "elevation_dp": _to_value(getattr(r, "elevation_dp", 0.0))
                        })

            # Sum all pressure drops
            total_dp_pa = 0.0
            for r in comp_list:
                total_dp_pa += _to_value(r.get("pressure_drop_Pa", r.get("pressure_drop", 0.0)), prefer_unit="Pa")
                total_dp_pa += _to_value(r.get("minor_dp", 0.0), prefer_unit="Pa")
                total_dp_pa += _to_value(r.get("elevation_dp", 0.0), prefer_unit="Pa")

            # Fluid density
            rho_obj = self._get_density() if hasattr(self, "_get_density") else getattr(fluid, "density", 1000.0)
            rho = _to_value(rho_obj() if callable(rho_obj) else rho_obj, prefer_unit="kg/m3")

            # Head loss and pump power
            total_head_m = total_dp_pa / (rho * G) if rho else float("inf")
            pump_eff = self.data.get("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
            shaft_power_kw = (total_dp_pa * q_in.value) / (1000.0 * pump_eff) if pump_eff else 0.0

            # Store results
            results_out.update({
                "mode": "network",
                "summary": {
                    "inlet_flow_m3s": q_in.value,
                    "total_pressure_drop_Pa": total_dp_pa,
                    "total_head_m": total_head_m,
                    "pump_shaft_power_kW": shaft_power_kw,
                    "solver_converged": solved_dict.get("success", False),
                    "solver_iterations": solved_dict.get("iterations", getattr(solver_meta, "iterations", None)),
                },
                "components": comp_list
            })
        # -----------------------
        # SINGLE PIPE MODE
        # -----------------------
        else:
            pipe_instance = self._ensure_pipe_object()
            setattr(pipe_instance, "fittings", self.data.get("fittings", []))

            if diameter is None:
                # Solve for optimum diameter based on available_dp
                self.data.update({
                    "pipe": pipe_instance,
                    "fluid": fluid,
                    "available_dp": available_dp,
                })
                pr = self._solve_for_diameter(**self.data)
                self._results = pr
                return pr

            # Diameter provided → calculate
            pipe_instance.internal_diameter = _ensure_diameter_obj(diameter)
            calc = self._pipe_calculation(pipe_instance, q_in)

            D_final = self._resolve_internal_diameter(pipe_instance)
            total_dp_pa = _to_value(calc.get("pressure_drop", 0.0), prefer_unit="Pa")
            total_dp_pa += _to_value(calc.get("minor_dp", 0.0), prefer_unit="Pa")
            total_dp_pa += _to_value(calc.get("elevation_dp", 0.0), prefer_unit="Pa")

            rho_val = _to_value(fluid.density(), prefer_unit="kg/m3")
            total_head_m = total_dp_pa / (rho_val * G) if rho_val else float("inf")
            shaft_power_kw = (total_dp_pa * q_in.value) / (1000.0 * pump_eff)
            velocity_val = _to_value(calc.get("velocity"), prefer_unit="m/s")

            results_out.update({
                "mode": "single_pipe",
                "summary": {
                    "flow_m3s": q_in.value,
                    "total_pressure_drop_Pa": total_dp_pa,
                    "total_head_m": total_head_m,
                    "pump_shaft_power_kW": shaft_power_kw,
                    "velocity": velocity_val,
                    "reynolds": calc.get("reynolds"),
                    "friction_factor": calc.get("friction_factor"),
                    "calculated_diameter_m": D_final.value,
                },
                "components": [{
                    "type": "pipe",
                    "name": pipe_instance.name,
                    "length": pipe_instance.length,
                    "diameter": D_final,
                    "velocity": velocity_val,
                    "reynolds": calc.get("reynolds"),
                    "friction_factor": calc.get("friction_factor"),
                    "major_dp": calc.get("major_dp"),
                    "minor_dp": calc.get("minor_dp"),
                    "elevation_dp": calc.get("elevation_dp"),
                    "total_dp": total_dp_pa,
                }],
            })

        # Store consistent PipelineResults
        self._results = PipelineResults(results_out)
        return self._results





    def summary(self) -> Optional[PipelineResults]:
        """
        Returns the summary of the last run.
        """
        if not self._results:
            print("No results available for summary.")
            return None
        return self._results.summary()

    # ---------------------- Backwards compatibility / helpers ---------------
    def _ensure_pipe_object(self) -> Pipe:
        """
        Constructs a Pipe object from engine data if not provided.
        """
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
    def _internal_diameter_m(self, element: Any = None) -> Diameter:
        """
        Returns the nominal internal diameter as a Diameter object in meters.
        Handles Pipe, Fitting (via parent pipe), and falls back to a default value.
        """
        if element is None:
            # fallback: default diameter
            return Diameter(0.1, "m")

        if hasattr(element, "nominal_diameter"):
            d = element.nominal_diameter
            if isinstance(d, Diameter):
                return d.to("m")
            elif isinstance(d, (int, float)):
                return Diameter(d, "m")  # wrap float in Diameter
            else:
                raise TypeError(f"Unsupported diameter type: {type(d)}")

        # For Fitting, use parent pipe
        if isinstance(element, Fitting) and hasattr(element, "parent_pipe") and element.parent_pipe is not None:
            return self._internal_diameter_m(element.parent_pipe)

        # fallback
        return Diameter(0.1, "m")


    
    
    
    def _resolve_internal_diameter(self, pipe: Pipe) -> Diameter:
        """
        Return internal diameter as a Diameter object, safely.

        Args:
            pipe (Pipe): The pipe object to get the diameter from.

        Returns:
            Diameter: The resolved diameter object.
        """
        if getattr(pipe, "internal_diameter", None):
            return pipe.internal_diameter
        if getattr(pipe, "nominal_diameter", None):
            d = pipe.nominal_diameter
            return d if isinstance(d, Diameter) else Diameter(float(d), "m")
        if getattr(self, "diameter", None):
            d = self.diameter
            return d if isinstance(d, Diameter) else Diameter(float(d), "m")

        # compute optimum and pick nearest standard
        opt_d = OptimumPipeDiameter(flow_rate=self._infer_flowrate(), density=self._get_density()).calculate()
        _, std_d = self._select_standard_diameter(opt_d.to("m").value)
        return std_d


    def _select_standard_diameter(self, ideal_d_m: float) -> Tuple[str, Diameter]:
        """
        Maps a continuous ideal diameter (m) to the nearest standard nominal pipe size.

        Always returns (label, Diameter), never a raw float.
        Picks the smallest standard size that is >= ideal_d_m.

        Args:
            ideal_d_m (float): The ideal diameter in meters.

        Returns:
            Tuple[str, Diameter]: The label and the Diameter object.

        Raises:
            ValueError: If no standard pipe diameters are available.
        """
        candidates: List[Tuple[str, Diameter]] = []

        for nominal in list_available_pipe_diameters():
            try:
                d_internal = nominal  # already a Diameter object
                if not isinstance(d_internal, Diameter):
                    d_internal = Diameter(float(d_internal), "m")
                candidates.append((f"{nominal} mm", d_internal))
            except Exception:
                continue

        # sort ascending by internal diameter
        candidates.sort(key=lambda x: x[1].to("m").value)

        for label, d in candidates:
            if d.to("m").value >= ideal_d_m:
                return label, d

        # fallback: return largest available
        if candidates:
            return candidates[-1][0], candidates[-1][1]

        raise ValueError("No standard pipe diameters available in catalog")
    


    def _solve_for_diameter(self, **kwargs):
        """
        Sizing a single pipeline to meet either a target velocity or an available pressure drop.
        The function iteratively tests all standard pipe sizes to find the best fit.
        """
        
        # helpers for units/values
        def _to_value(obj, attr="value"):
            """Return numeric value for your unit wrappers (Pressure, Variable, Diameter, etc.)."""
            if obj is None:
                return None
            if hasattr(obj, "to"):
                for unit in ("Pa", "m", "m^3/s", "m3/s", "in"):
                    try:
                        converted = obj.to(unit)
                        if hasattr(converted, "value"):
                            return float(converted.value)
                    except Exception:
                        continue
            if hasattr(obj, "value"):
                return float(obj.value)
            try:
                return float(obj)
            except Exception:
                return None

        def _pressure_to_Pa(p):
            """Accept Pressure, Variable, numeric and return Pa float."""
            if p is None:
                return None
            if hasattr(p, "to"):
                try:
                    return float(p.to("Pa").value)
                except Exception:
                    pass
            if hasattr(p, "value"):
                return float(p.value)
            try:
                return float(p)
            except Exception:
                return None
        
        # Inputs
        fluid = kwargs.get("fluid") or self.data.get("fluid")
        flow_rate = self._infer_flowrate()
        available_dp = kwargs.get("available_dp") or self.data.get("available_dp")
        pump_eff = kwargs.get("pump_efficiency", self.data.get("pump_efficiency", 0.75))
        G = 9.80665
        
        if not fluid or not flow_rate:
            raise ValueError("flow_rate and fluid are required for diameter sizing.")
        
        pipe = self._ensure_pipe_object()
        q_val = _to_value(flow_rate)
        
        # Define velocity range globally
        vel_range = get_recommended_velocity(getattr(fluid, "name", "").strip().lower().replace(" ", "_"))
        if vel_range is None:
            v_min, v_max = 0.5, 100.0
        elif isinstance(vel_range, tuple):
            v_min, v_max = vel_range
        else:
            v_min = v_max = float(vel_range)

        available_dp_pa = _pressure_to_Pa(available_dp)
        
        if available_dp_pa is not None:
            all_standard_diameters = list_available_pipe_diameters()
            best_result = None
        
            # Step 1: Solve for Diameter using Major Losses Only
            for D_test in all_standard_diameters:
                pipe_sizing_temp = Pipe(
                    name=pipe.name,
                    length=pipe.length,
                    material=pipe.material,
                    nominal_diameter=D_test,
                    fittings=[] # Sizing with no fittings
                )
                
                calc = self._pipe_calculation(pipe_sizing_temp, flow_rate)
                pd_major_pa = _pressure_to_Pa(calc.get("major_dp"))

                if pd_major_pa is not None and pd_major_pa <= available_dp_pa:
                    best_result = {
                        "diameter": D_test,
                        "major_dp_pa": pd_major_pa,
                    }
                    break
            
            # If no feasible solution, fall back to largest pipe size
            if best_result is None and all_standard_diameters:
                D_test = all_standard_diameters[-1]
                best_result = {"diameter": D_test}
            
            if best_result is None:
                raise RuntimeError("No suitable diameter found among standard sizes.")

            D_final = best_result["diameter"]
            
            # Step 2: Finalize Calculations with All Losses
            final_pipe_object = Pipe(
                name=pipe.name,
                length=pipe.length,
                material=pipe.material,
                nominal_diameter=D_final,
                fittings=self.data.get("fittings", []) or [] # Ensure fittings are included
            )
            final_calc = self._pipe_calculation(final_pipe_object, flow_rate)
            total_dp_pa = _pressure_to_Pa(final_calc.get("pressure_drop"))
            v_final = _to_value(final_calc.get("velocity"))

            print(f"✅ Found optimal diameter for available pressure drop.")
            print(f"   Selected Diameter: {D_final.to('in')} ({D_final.value:.3f} m)")
            print(f"   Calculated Pressure Drop: {total_dp_pa:.2f} Pa (allowed: {available_dp_pa:.2f} Pa)")

        else:
            # Velocity-based sizing (no change from previous correct version)
            v_start = 0.5 * (v_min + v_max)
            D_initial = math.sqrt(max(1e-20, 4.0 * q_val / (math.pi * v_start)))
            #print("D_initial:", D_initial)
            selected_diameter_obj = None
            all_standard_diameters = list_available_pipe_diameters()
            #all_standard_internal_diameters = 
            for d in all_standard_diameters:
                #print("Nominal Dia:", d)
                d = get_internal_diameter(nominal_diameter = d)
                d_m = _to_value(d)
                #print("Internal Diameter:", d_m)
                if d_m is not None and d_m >= D_initial:
                    selected_diameter_obj = d
                    #print("Selected Diameter:", d)
                    break
            if selected_diameter_obj is None and all_standard_diameters:
                selected_diameter_obj = all_standard_diameters[-1]
            
            final_pipe_object = Pipe(
                name=pipe.name,
                length=pipe.length,
                material=pipe.material,
                nominal_diameter=get_nominal_dia_from_internal_dia(selected_diameter_obj),
                fittings=self.data.get("fittings", []) or []
            )
            #print("Final Pipe Object:", final_pipe_object.nominal_diameter)
            final_calc = self._pipe_calculation(final_pipe_object, flow_rate)
            
            D_final = get_nominal_dia_from_internal_dia(selected_diameter_obj)
            total_dp_pa = _pressure_to_Pa(final_calc.get("pressure_drop"))
            v_final = _to_value(final_calc.get("velocity"))
            
            print(f"✅ Found optimal diameter based on recommended velocity.")
            print(f"   Selected Diameter: {D_final.to('in')} ")
            print(f"   Calculated Pressure Drop: {total_dp_pa:.2f} Pa")

        # Final computations and return value (no change from previous correct version)
        total_dp_pa = total_dp_pa or 0.0
        dens_obj = getattr(fluid, "density", 1000.0)
        if callable(dens_obj):
            dens_obj = dens_obj()
        rho_val = float(getattr(dens_obj, "value", dens_obj) or 1000.0)
        total_head_m = total_dp_pa / (rho_val * G) if rho_val else float("inf")
        shaft_power_kw = (total_dp_pa * q_val) / (1000.0 * pump_eff) if q_val and pump_eff else 0.0
        v_final = v_final or _to_value(final_calc.get("velocity"))
        
        if v_final is not None and not (v_min <= v_final <= v_max):
            print(
                f"⚠️ Warning: Final velocity {v_final:.2f} m/s outside recommended "
                f"range ({v_min:.2f}-{v_max:.2f} m/s) for {getattr(fluid, 'name', 'fluid')}."
            )
        self.selected_diameter = D_final
        results_out = {
            "network_name": pipe.name,
            "mode": "single_pipe",
            "summary": {
                "flow_m3s": q_val,
                "total_pressure_drop_Pa": total_dp_pa,
                "total_head_m": total_head_m,
                "pump_shaft_power_kW": shaft_power_kw,
                "velocity": v_final,
                "reynolds": final_calc.get("reynolds"),
                "friction_factor": final_calc.get("friction_factor"),
                "calculated_diameter_m": D_final.to("m").value,
            },
            "components": [
                {
                    "type": "pipe",
                    "name": pipe.name,
                    "length": pipe.length,
                    "diameter": D_final,
                    "velocity": v_final,
                    "reynolds": final_calc.get("reynolds"),
                    "friction_factor": final_calc.get("friction_factor"),
                    "major_dp": final_calc.get("major_dp"),
                    "minor_dp": final_calc.get("minor_dp"),
                    "elevation_dp": final_calc.get("elevation_dp"),
                    "pressure_drop": final_calc.get("pressure_drop"),
                }
            ],
        }
        return PipelineResults(results_out)

    
    def _solve_for_diameter_network(self, network, **kwargs):
        """
        Iteratively sizes each pipe in a network using the same standard diameter
        selection logic as `_solve_for_diameter`, ensuring consistency between
        single-pipe and network sizing.
        """
        import math
        from ..pipelines.standards import get_recommended_velocity, list_available_pipe_diameters
        G = 9.80665
    
        fluid = kwargs.get("fluid") or self.data.get("fluid")
        if not fluid:
            raise ValueError("Fluid must be provided for network diameter sizing.")
    
        available_dp = kwargs.get("available_dp") or self.data.get("available_dp")
        pump_eff = kwargs.get("pump_efficiency", self.data.get("pump_efficiency", 0.75))
    
        all_results = []
    
        for pipe in getattr(network, "pipes", []):
            flow_rate = self._infer_flowrate(pipe)
            if not flow_rate:
                continue
    
            q_val = float(flow_rate.value)
    
            # Recommended velocity range
            vel_range = get_recommended_velocity(getattr(fluid, "name", "").strip().lower().replace(" ", "_"))
            if vel_range is None:
                v_min, v_max = 0.5, 100.0
            elif isinstance(vel_range, tuple):
                v_min, v_max = vel_range
            else:
                v_min = v_max = float(vel_range)
    
            # Initial diameter guess
            v_start = 0.5 * (v_min + v_max)
            D_initial = math.sqrt(max(1e-20, 4.0 * q_val / (math.pi * v_start)))
    
            # Standard diameters list
            std_diams = list_available_pipe_diameters()
            D_candidates = []
            for idx, d in enumerate(std_diams):
                d_m = d.to("m").value
                if d_m >= D_initial:
                    D_candidates = [
                        std_diams[idx - 1] if idx > 0 else None,
                        d,
                        std_diams[idx + 1] if idx < len(std_diams) - 1 else None
                    ]
                    break
            D_candidates = [d for d in D_candidates if d is not None]
    
            if not D_candidates:
                D_candidates = [std_diams[-1]]
    
            results_list = []
            for D_test in D_candidates:
                pipe.internal_diameter = D_test
                calc = self._pipe_calculation(pipe, flow_rate)
                results_list.append({
                    "diameter": D_test,
                    "diameter_m": D_test.to("m").value,
                    "calc": calc,
                    "pressure_drop_Pa": calc["pressure_drop"].to("Pa").value if hasattr(calc["pressure_drop"], "to") else calc["pressure_drop"],
                    "velocity_m_s": calc["velocity"].to("m/s").value if hasattr(calc["velocity"], "to") else calc["velocity"],
                })
    
            # Selection logic
            if available_dp:
                available_dp_pa = available_dp.to("Pa").value if hasattr(available_dp, "to") else float(available_dp)
                feasible = [r for r in results_list if r["pressure_drop_Pa"] <= available_dp_pa]
                if feasible:
                    best_result = min(feasible, key=lambda r: r["diameter_m"])
                else:
                    best_result = min(results_list, key=lambda r: (abs(r["pressure_drop_Pa"] - available_dp_pa), -r["diameter_m"]))
            else:
                print(f"🔍 Pipe {pipe.name}: No available DP provided. Showing candidates:")
                for r in results_list:
                    print(f"  {r['diameter'].to('in')} -> {r['velocity_m_s']:.2f} m/s, {r['pressure_drop_Pa']:.2f} Pa")
                best_result = results_list[len(results_list)//2]
    
            pipe.internal_diameter = best_result["diameter"]
            final_calc = best_result["calc"]
            total_dp_pa = best_result["pressure_drop_Pa"]
    
            # Compute head and power
            dens_obj = fluid.density() if callable(fluid.density) else fluid.density
            rho_val = float(dens_obj.to("kg/m3").value if hasattr(dens_obj, "to") else dens_obj)
            total_head_m = total_dp_pa / (rho_val * G)
            shaft_power_kw = (total_dp_pa * q_val) / (1000.0 * pump_eff)
    
            # Warning if velocity out of range
            v_final = best_result["velocity_m_s"]
            if not (v_min <= v_final <= v_max):
                print(f"⚠️ Warning: Pipe '{pipe.name}' velocity {v_final:.2f} m/s outside recommended range {v_min}-{v_max} m/s")
    
            all_results.append({
                "network_name": pipe.name,
                "mode": "network_pipe",
                "summary": {
                    "flow_m3s": q_val,
                    "total_pressure_drop_Pa": total_dp_pa,
                    "total_head_m": total_head_m,
                    "pump_shaft_power_kW": shaft_power_kw,
                    "velocity": v_final,
                    "reynolds": final_calc.get("reynolds"),
                    "friction_factor": final_calc.get("friction_factor"),
                    "calculated_diameter_m": best_result["diameter"].to("m").value,
                },
                "components": [{
                    "type": "pipe",
                    "name": pipe.name,
                    "length": pipe.length,
                    "diameter": best_result["diameter"],
                    "velocity": v_final,
                    "reynolds": final_calc.get("reynolds"),
                    "friction_factor": final_calc.get("friction_factor"),
                    "major_dp": final_calc.get("major_dp"),
                    "minor_dp": final_calc.get("minor_dp"),
                    "elevation_dp": final_calc.get("elevation_dp"),
                    "total_dp": final_calc.get("pressure_drop"),
                }],
            })
    
        return PipelineResults({"all_simulation_results": all_results})

