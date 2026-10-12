# processpi/pipelines/engine.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import math
import warnings

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
from .pumps import Pump
from .vessel import Vessel
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
# Element types that can sit inline in a branch and be evaluated by the engine.
INLINE_ELEMENTS = (Pipe, Pump, Equipment, Vessel, Fitting)

# ------------------------------- Helpers -----------------------------------


def _elevation_m(node: Any) -> float:
    """
    Elevation of a network node in metres.

    A node without an elevation counts as 0 m. A Length is taken in metres; any
    other value must be a plain number. Anything else raises, because treating
    it as 0 m would silently drop the static head from the pressure balance.
    """
    elevation = getattr(node, "elevation", None)
    if elevation is None:
        return 0.0
    if isinstance(elevation, Variable):
        # Units objects hold their SI base value (metres for a Length).
        return float(elevation.value)
    try:
        return float(elevation)
    except (TypeError, ValueError):
        raise TypeError(
            f"Node elevation must be a number in metres or a Length, got {elevation!r}"
        ) from None


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
        eps = get_roughness(material) if material else 0.0
        return ColebrookWhite(reynolds_number=Re, roughness=eps, diameter=d).calculate()

    def _major_dp_pa(self, f: float, L: Length, d: Diameter, v: Velocity) -> Pressure:
        """
        Calculates the major pressure drop (friction loss) using the Darcy-Weisbach equation.
        """
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
        if K is not None:
            return Pressure(0.5 * rho * v_val * v_val * float(K), "Pa")
        
        # 2. Try explicit equivalent length on the fitting
        Le_candidate = getattr(fitting, "Le", None) or getattr(fitting, "equivalent_length", None) or getattr(fitting, "total_Le", None)
        # Perform the Le/D calculation if an equivalent length value was found
        if Le_candidate is not None:
            le_val = None
            if isinstance(Le_candidate, Length):
                le_val = Le_candidate.to("m").value
            elif callable(Le_candidate):
                # Check if the method call returns a value before using it
                le_result = Le_candidate()
                if le_result is not None:
                    le_val = le_result * d.to("m").value
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
                return Length(le_val, "m")

        # 3. Fallback to standards lookup (for K-factor) if no explicit Le/D was found
        fitting_type = getattr(fitting, "fitting_type", None)
        if fitting_type is not None:
            Re = self._reynolds(v, d)
            pipe = self.data.get("pipe")
            roughness = get_roughness(getattr(pipe, "material", None))
            
            d_m = d.to("m").value
            # get_roughness gives a plain Variable in mm.
            eps_m = float(getattr(roughness, "value", roughness)) / 1000.0
            relative_roughness = eps_m / d_m if d_m > 0 else None
            K_from_standards = get_k_factor(fitting_type, Re, relative_roughness, d_m)
            if K_from_standards is not None:
                return Pressure(0.5 * rho * v_val * v_val * float(K_from_standards), "Pa")
            else:
                warnings.warn(
                    f"No standard K-factor or equivalent length found for fitting type "
                    f"'{fitting_type}'; it adds no pressure drop.",
                    UserWarning,
                    stacklevel=2,
                )

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
        Re = self._reynolds(v, d)
        material = getattr(pipe, "material", None)
        method = self.data.get("method", "darcy_weisbach").lower()

        if getattr(Re, "value", Re) <= 1e-8:
            f = 0.0
            dp_major = self._major_dp_pa(f, pipe.length or Length(1.0, "m"), d, v)
        elif method == "hazen_williams":
            hw_coeff = getattr(pipe, "hw_coefficient", None) or self.data.get("hw_coefficient", 130.0)
            dp_major = PressureDropHazenWilliams(
                length=pipe.length or Length(1.0, "m"),
                flow_rate=q_used,
                coefficient=hw_coeff,
                diameter=d,
                density=self._get_density(),
            ).calculate()
            f = None
        else:
            f = self._friction_factor(Re, d, material=pipe.material)
            dp_major = self._major_dp_pa(f, pipe.length or Length(1.0, "m"), d, v)
        # ---------------------------
        # Minor Losses (always included)
        # ---------------------------
        dp_minor = Pressure(0.0, "Pa")
        ft = getattr(pipe, "fittings", []) or [] or getattr(self.data.get("pipe"), "fittings", []) or [] or getattr(self.data.get("fittings"), "fittings", []) or []
        # Hazen-Williams has no friction factor, but the fitting losses are
        # Darcy-Weisbach on an equivalent length; with f None they raised
        # "Could not interpret friction_factor value: None".
        f_minor = f
        if f_minor is None and ft:
            f_minor = self._friction_factor(Re, d, material=pipe.material)
        for ft in ft:
            ft.diameter = d
            le_val = self._minor_dp_pa(ft, v, f_minor, d)
            equivalent_length = Length(0.0, "m")
            if isinstance(le_val, Length):
                equivalent_length = le_val.value * ft.quantity
                dp_minor += self._major_dp_pa(f_minor, equivalent_length, d, v)
            elif isinstance(le_val, Pressure):
                dp_minor += le_val
            else:
                # If neither Length nor Pressure, skip or handle as needed
                pass
        # ---------------------------
        # Elevation Loss
        # ---------------------------
        rho_val = self._get_density().value
        start_node = getattr(pipe, "start_node", None)
        end_node = getattr(pipe, "end_node", None)
        elev_diff_m = _elevation_m(end_node) - _elevation_m(start_node)
        # Pressure cannot hold a negative value, so a downhill pipe gets no
        # credit for the static head it gains (as before, when the ValueError
        # was swallowed). How to report a pressure gain is an open question.
        elev_loss = Pressure(rho_val * G * max(elev_diff_m, 0.0), "Pa")

        # ---------------------------
        # Total Pressure Drop
        # ---------------------------
        total_dp_pa = sum(getattr(x, "value", x) for x in [dp_major, dp_minor, elev_loss])
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


    def _compute_network(
        self,
        network: Any,
        flow_rate: Optional[VolumetricFlowRate] = None
    ) -> Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Compute total pressure drop for a network, including major, minor, and elevation losses.

        Series blocks add their element pressure drops. Parallel blocks share a
        single pressure drop: the flow is split between the branches until every
        branch sees the same drop, and that common value is the block's drop.

        Args:
            network (Any): An inline element (see ``INLINE_ELEMENTS``), a list of
                        elements (series branch), a list of branches (each branch a
                        list, treated as parallel), or a PipelineNetwork object.
            flow_rate (Optional[VolumetricFlowRate]): The flow rate entering the network.

        Returns:
            Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
                - total network pressure drop (clamped at zero, see the summary key
                  ``total_pressure_drop_Pa`` for the signed value)
                - element reports (major + minor + elevation)
                - network summary
        """
        q = flow_rate if flow_rate is not None else self._infer_flowrate()
        total_dp_pa, element_reports, meta = self._evaluate_block(network, q)

        # `Pressure` rejects negative values, so a network whose pumps more than
        # cover its friction is clamped to zero in the returned object. The signed
        # value is always available as `total_pressure_drop_Pa` in the summary.
        total_dp_obj = Pressure(max(total_dp_pa, 0.0), "Pa")

        network_summary = {
            "total_pressure_drop": total_dp_obj,
            "total_pressure_drop_Pa": total_dp_pa,
            "number_of_branches": meta.get("number_of_branches", 1),
            "number_of_elements": len(element_reports),
            "converged": meta.get("converged", True),
            "iterations": meta.get("iterations", 0),
            "branch_flows": meta.get("branch_flows"),
            "elements": element_reports,
        }

        return total_dp_obj, element_reports, network_summary

    def _evaluate_block(
        self,
        block: Any,
        flow_rate: VolumetricFlowRate,
        branch_index: int = 0,
    ) -> Tuple[float, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Recursively evaluate a network block at a given flow rate.

        Args:
            block (Any): An inline element (see ``INLINE_ELEMENTS``), a list, or
                a PipelineNetwork.
            flow_rate (VolumetricFlowRate): Flow entering the block.
            branch_index (int): Index tagged onto the element reports produced here.

        Returns:
            Tuple[float, List[Dict[str, Any]], Dict[str, Any]]:
                - pressure drop across the block in Pa (negative for a net gain)
                - element reports
                - meta: ``converged``, ``iterations``, ``number_of_branches`` and,
                  for a parallel block, the resolved ``branch_flows`` in m3/s
        """
        series_meta = {"converged": True, "iterations": 0, "number_of_branches": 1,
                       "branch_flows": None}

        # --- single elements ---------------------------------------------
        if isinstance(block, Pipe):
            calc = self._pipe_calculation(block, flow_rate)
            dp_pa = getattr(calc["pressure_drop"], "value", calc["pressure_drop"])
            report = {
                "name": getattr(block, "name", f"Pipe_{id(block)}"),
                "type": "pipe",
                "diameter": calc["diameter"],
                "velocity": calc["velocity"],
                "reynolds": calc["reynolds"],
                "friction_factor": calc["friction_factor"],
                "major_dp": calc["major_dp"],
                "minor_dp": calc["minor_dp"],
                "elevation_dp": calc["elevation_dp"],
                "total_dp": calc["pressure_drop"],
                "pressure_drop_Pa": dp_pa,
                "flow_m3s": getattr(flow_rate, "value", flow_rate),
                "branch_index": branch_index,
            }
            return dp_pa, [report], series_meta

        if isinstance(block, Pump):
            gain_pa = self._pump_gain_pa(block).to("Pa").value
            head = getattr(block, "head", None)
            report = {
                "name": getattr(block, "name", f"Pump_{id(block)}"),
                "type": "pump",
                # A pump raises the pressure, so its contribution to the network
                # drop is negative. `Pressure` cannot hold that, so the signed
                # value is a plain float in Pa.
                "pressure_gain": Pressure(max(gain_pa, 0.0), "Pa"),
                "pressure_drop_Pa": -gain_pa,
                "head_m": head.to("m").value if hasattr(head, "to") else head,
                "flow_m3s": getattr(flow_rate, "value", flow_rate),
                "branch_index": branch_index,
            }
            return -gain_pa, [report], series_meta

        if isinstance(block, Equipment):
            dp_pa = self._equipment_dp_pa(block).to("Pa").value
            report = {
                "name": getattr(block, "name", f"Equipment_{id(block)}"),
                "type": "equipment",
                "total_dp": Pressure(dp_pa, "Pa"),
                "pressure_drop_Pa": dp_pa,
                "flow_m3s": getattr(flow_rate, "value", flow_rate),
                "branch_index": branch_index,
            }
            return dp_pa, [report], series_meta

        if isinstance(block, Vessel):
            # A vessel is a hold-up point, not an inline resistance.
            report = {
                "name": getattr(block, "name", f"Vessel_{id(block)}"),
                "type": "vessel",
                "total_dp": Pressure(0.0, "Pa"),
                "pressure_drop_Pa": 0.0,
                "flow_m3s": getattr(flow_rate, "value", flow_rate),
                "branch_index": branch_index,
            }
            return 0.0, [report], series_meta

        if isinstance(block, Fitting):
            # A fitting added at a node has no pipe to take its velocity and
            # friction factor from, so its loss is not modelled here. Put it in the
            # `fittings` list of the pipe it belongs to and it is counted as a
            # minor loss of that pipe.
            report = {
                "name": getattr(block, "fitting_type", f"Fitting_{id(block)}"),
                "type": "fitting",
                "total_dp": Pressure(0.0, "Pa"),
                "pressure_drop_Pa": 0.0,
                "flow_m3s": getattr(flow_rate, "value", flow_rate),
                "branch_index": branch_index,
                "warnings": [
                    "Node-level fitting is not modelled inline; add it to the "
                    "`fittings` list of the adjoining pipe to include its loss."
                ],
            }
            return 0.0, [report], series_meta

        # --- plain lists --------------------------------------------------
        if isinstance(block, list):
            if not block:
                return 0.0, [], series_meta
            if all(isinstance(b, list) for b in block):
                # A list of branches is a parallel set.
                return self._evaluate_parallel(block, flow_rate, branch_index)
            if any(isinstance(b, list) for b in block):
                raise TypeError(
                    "Network list must contain either elements (a series branch) "
                    "or lists of elements (parallel branches), not a mix"
                )
            return self._evaluate_series(block, flow_rate, branch_index)

        # --- networks -----------------------------------------------------
        if isinstance(block, PipelineNetwork):
            if block.connection_type == "parallel":
                return self._evaluate_parallel(
                    block.elements, flow_rate, branch_index, net_name=block.name
                )
            return self._evaluate_series(block.elements, flow_rate, branch_index)

        raise TypeError(
            "Network must be a Pipe, Pump, Equipment, Vessel, Fitting, list of "
            f"elements/branches, or PipelineNetwork object, not {type(block).__name__}"
        )

    def _evaluate_series(
        self,
        elements: List[Any],
        flow_rate: VolumetricFlowRate,
        branch_index: int = 0,
    ) -> Tuple[float, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Evaluate elements in series: same flow through each, pressure drops add.
        """
        total_dp_pa = 0.0
        reports: List[Dict[str, Any]] = []
        converged = True
        iterations = 0

        for element in elements:
            dp_pa, el_reports, meta = self._evaluate_block(element, flow_rate, branch_index)
            total_dp_pa += dp_pa
            reports.extend(el_reports)
            converged = converged and meta.get("converged", True)
            iterations = max(iterations, meta.get("iterations", 0))

        return total_dp_pa, reports, {
            "converged": converged,
            "iterations": iterations,
            "number_of_branches": 1,
            "branch_flows": None,
        }

    def _evaluate_parallel(
        self,
        branches: List[Any],
        flow_rate: VolumetricFlowRate,
        branch_index: int = 0,
        net_name: Optional[str] = None,
    ) -> Tuple[float, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Evaluate branches in parallel: the flow splits, the pressure drop is shared.

        The split is resolved by :meth:`_balance_parallel_flows`; the block drop is
        the mean of the balanced branch drops, which is the common drop once the
        iteration has converged.
        """
        if not branches:
            return 0.0, [], {"converged": True, "iterations": 0,
                             "number_of_branches": 0, "branch_flows": []}
        if len(branches) == 1:
            dp_pa, reports, meta = self._evaluate_block(branches[0], flow_rate, branch_index)
            meta = dict(meta)
            meta["number_of_branches"] = 1
            meta["branch_flows"] = [getattr(flow_rate, "value", flow_rate)]
            return dp_pa, reports, meta

        flows, dps, converged, iterations = self._balance_parallel_flows(
            branches, flow_rate, net_name=net_name
        )

        reports: List[Dict[str, Any]] = []
        for idx, (branch, q_branch) in enumerate(zip(branches, flows)):
            _, br_reports, _ = self._evaluate_block(
                branch, VolumetricFlowRate(q_branch, "m3/s"), branch_index + idx
            )
            reports.extend(br_reports)

        # Parallel branches share one pressure drop, they do not add up.
        block_dp_pa = sum(dps) / len(dps)

        return block_dp_pa, reports, {
            "converged": converged,
            "iterations": iterations,
            "number_of_branches": len(branches),
            "branch_flows": flows,
        }

    def _balance_parallel_flows(
        self,
        branches: List[Any],
        q_total: VolumetricFlowRate,
        net_name: Optional[str] = None,
        tol: float = 1e-4,
        max_iter: int = 100,
    ) -> Tuple[List[float], List[float], bool, int]:
        """
        Split a total flow between parallel branches so that every branch sees the
        same pressure drop.

        Turbulent branch drop scales roughly as q^2, so the update is
        ``q_i <- q_i * sqrt(dp_mean / dp_i)`` followed by a rescale to ``q_total``,
        which conserves mass on every iteration. Convergence is measured on the
        spread of the branch drops, not on the size of the flow correction.

        Args:
            branches (List[Any]): The parallel branches.
            q_total (VolumetricFlowRate): Total flow entering the block.
            net_name (Optional[str]): Name of the parallel network, used to look up
                a user-supplied split in ``self.data["flow_split"]``.
            tol (float): Relative tolerance on the branch pressure drop spread.
            max_iter (int): Maximum number of iterations.

        Returns:
            Tuple[List[float], List[float], bool, int]:
                branch flows (m3/s), branch pressure drops (Pa), whether the
                iteration converged, and the number of iterations used.
        """
        n = len(branches)
        q_total_val = float(getattr(q_total, "value", q_total))
        flows = [q_total_val / n] * n

        # A user-supplied split fixes the flows; only the drops are then computed.
        split_cfg = (self.data.get("flow_split") or {}).get(net_name) if net_name else None
        if split_cfg and len(split_cfg) == n:
            vals = [float(x) for x in split_cfg]
            s = sum(vals) or 1.0
            flows = [q_total_val * (v / s) for v in vals]
            dps = [
                self._evaluate_block(branch, VolumetricFlowRate(q, "m3/s"))[0]
                for branch, q in zip(branches, flows)
            ]
            return flows, dps, True, 0

        dps = [0.0] * n
        iterations = 0
        for iterations in range(1, max_iter + 1):
            dps = [
                self._evaluate_block(branch, VolumetricFlowRate(q, "m3/s"))[0]
                for branch, q in zip(branches, flows)
            ]
            dp_mean = sum(dps) / n
            scale = max(abs(dp_mean), 1e-9)
            if max(abs(dp - dp_mean) for dp in dps) / scale < tol:
                return flows, dps, True, iterations

            # Only positive drops can be balanced by the q^2 law; a branch with a
            # net gain (a pump) or no loss at all is left at its current flow.
            if dp_mean <= 0 or any(dp <= 0 for dp in dps):
                return flows, dps, False, iterations

            updated = [q * math.sqrt(dp_mean / dp) for q, dp in zip(flows, dps)]
            s = sum(updated)
            if s <= 0:
                return flows, dps, False, iterations
            flows = [q * q_total_val / s for q in updated]

        return flows, dps, False, iterations


    # ---------------------- Network Solvers ---------------------------------


    def _solve_network_dual(self, network: Any, q_total: VolumetricFlowRate, tol: float = 1e-6) -> Tuple[Dict[str, Any], Any]:
        """
        Top-level solver for networks with multiple branches.

        Balances flows across parallel branches and adds drops along series
        branches, so that the returned ``total_dp_Pa`` is the drop from the network
        inlet to its outlet rather than a sum over every element.
        """
        _, reports, summary = self._compute_network(network, q_total)
        branch_flows = summary.get("branch_flows")
        if not branch_flows:
            branch_flows = [float(getattr(q_total, "value", q_total))]

        return {
            "success": summary.get("converged", True),
            "branch_flows": branch_flows,
            "reports": reports,
            "total_dp_Pa": summary.get("total_pressure_drop_Pa", 0.0),
            "iterations": summary.get("iterations", 0),
        }, None

    def _normalize_branches(self, network) -> list[list[Any]]:
        """
        Converts any PipelineNetwork or list of branches into a flat list of
        branches, where each branch is a list of inline elements (see
        ``INLINE_ELEMENTS``).

        Args:
            network (Any): The network or list of elements to normalize.

        Returns:
            list[list[Any]]: A flattened list of branches.

        Raises:
            TypeError: If the network contains an element type that cannot be
                placed in a branch.
        """
        if isinstance(network, INLINE_ELEMENTS):
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
                    if isinstance(el, INLINE_ELEMENTS):
                        series_branch.append(el)
                    elif isinstance(el, PipelineNetwork):
                        # Flatten nested series inside this branch
                        nested_branches = self._normalize_branches(el)
                        # For series, nested branch is appended to current branch
                        if nested_branches:
                            series_branch.extend(nested_branches[0])
                    else:
                        raise TypeError(
                            f"Element '{getattr(el, 'name', el)}' of type "
                            f"{type(el).__name__} cannot be part of a branch"
                        )
                branches.append(series_branch)
            elif network.connection_type == "parallel":
                # Each element is a separate branch
                for el in network.elements:
                    if isinstance(el, INLINE_ELEMENTS):
                        branches.append([el])
                    elif isinstance(el, PipelineNetwork):
                        nested = self._normalize_branches(el)
                        branches.extend(nested)
                    else:
                        raise TypeError(
                            f"Element '{getattr(el, 'name', el)}' of type "
                            f"{type(el).__name__} cannot be part of a branch"
                        )
            return branches
        else:
            raise TypeError(
                "Network must be an inline element, a list of elements/branches, "
                "or a PipelineNetwork-like object"
            )


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
        rho_obj = getattr(pump, "density", None)
        if rho_obj is None:
            rho = self._get_density().to("kg/m3").value
        elif hasattr(rho_obj, "to"):
            rho = rho_obj.to("kg/m3").value
        else:
            rho = float(rho_obj)

        pin = getattr(pump, "inlet_pressure", None)
        pout = getattr(pump, "outlet_pressure", None)
        if pin is not None and pout is not None:
            gain_pa = (
                self._as_pressure(pout).to("Pa").value
                - self._as_pressure(pin).to("Pa").value
            )
            if gain_pa < 0:
                raise ValueError(
                    f"Pump '{getattr(pump, 'name', '?')}' has an outlet pressure "
                    "below its inlet pressure"
                )
            return Pressure(gain_pa, "Pa")

        head = getattr(pump, "head", None)
        if head is not None:
            head_m = head.to("m").value if hasattr(head, "to") else float(head)
            return Pressure(rho * G * head_m, "Pa")
        return Pressure(0.0, "Pa")

    def _equipment_dp_pa(self, eq: Any) -> Pressure:
        """
        Converts Equipment pressure_drop (assumed bar) to Pa if needed.
        """
        dp = getattr(eq, "pressure_drop", 0.0) or 0.0
        return Pressure(float(dp), "bar").to("Pa") if not isinstance(dp, Pressure) else dp


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

            # Inlet-to-outlet drop from the solver. Element drops already include
            # their major, minor and elevation terms, and parallel branches share
            # one drop, so they must not be summed here.
            total_dp_pa = _to_value(solved_dict.get("total_dp_Pa", 0.0), prefer_unit="Pa")

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
            # "pressure_drop" is already major + minor + elevation.
            total_dp_pa = _to_value(calc.get("pressure_drop", 0.0), prefer_unit="Pa")

            rho_val = _to_value(fluid.density(), prefer_unit="kg/m3")
            total_head_m = total_dp_pa / (rho_val * G) if rho_val else float("inf")
            pump_eff = self.data.get("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
            shaft_power_kw = (total_dp_pa * q_in.value) / (1000.0 * pump_eff) if pump_eff else 0.0
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

    # ---------------------- Diameter helpers --------------------------------
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
                # The STD bore of the size; the nominal size itself used to be
                # returned as the internal diameter, labelled "4 in mm".
                d_internal = get_internal_diameter(nominal, "STD") or nominal
                if not isinstance(d_internal, Diameter):
                    d_internal = Diameter(float(d_internal), "m")
                candidates.append((str(nominal), d_internal))
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
        
        available_dp_met = None
        if available_dp_pa is not None:
            all_standard_diameters = list_available_pipe_diameters()
            if not all_standard_diameters:
                raise RuntimeError("No suitable diameter found among standard sizes.")
            fittings = self.data.get("fittings", []) or []

            # The smallest standard size whose whole pressure drop (pipe friction,
            # fittings and elevation) fits in the available drop. Sizing used to
            # test the pipe friction alone and then add the fittings without
            # checking again, so the size it called optimal could exceed the
            # available drop.
            D_final = None
            for D_test in all_standard_diameters:
                trial_pipe = Pipe(
                    name=pipe.name,
                    length=pipe.length,
                    material=pipe.material,
                    nominal_diameter=D_test,
                )
                # Pipe keeps a `fittings` keyword in its params; the loss
                # calculation reads the attribute.
                trial_pipe.fittings = fittings
                trial_calc = self._pipe_calculation(trial_pipe, flow_rate)
                trial_dp_pa = _pressure_to_Pa(trial_calc.get("pressure_drop"))
                if trial_dp_pa is not None and trial_dp_pa <= available_dp_pa:
                    D_final, final_pipe_object, final_calc = D_test, trial_pipe, trial_calc
                    break
            available_dp_met = D_final is not None

            if D_final is None:
                # Nothing fits: the largest size, reported as not meeting the drop.
                D_final = all_standard_diameters[-1]
                final_pipe_object = Pipe(
                    name=pipe.name,
                    length=pipe.length,
                    material=pipe.material,
                    nominal_diameter=D_final,
                )
                final_pipe_object.fittings = fittings
                final_calc = self._pipe_calculation(final_pipe_object, flow_rate)
            total_dp_pa = _pressure_to_Pa(final_calc.get("pressure_drop"))
            v_final = _to_value(final_calc.get("velocity"))

            if available_dp_met:
                print(f"✅ Found optimal diameter for available pressure drop.")
            else:
                print(f"⚠️ No standard size meets the available pressure drop; using the largest.")
            print(f"   Selected Diameter: {D_final.to('in')} ({final_pipe_object.internal_diameter.to('m').value:.4f} m internal)")
            print(f"   Calculated Pressure Drop: {total_dp_pa:.2f} Pa (allowed: {available_dp_pa:.2f} Pa)")

        else:
            # Velocity-based sizing (no change from previous correct version)
            v_start = 0.5 * (v_min + v_max)
            D_initial = math.sqrt(max(1e-20, 4.0 * q_val / (math.pi * v_start)))
            selected_diameter_obj = None
            all_standard_diameters = list_available_pipe_diameters()
            #all_standard_internal_diameters = 
            for d in all_standard_diameters:
                d = get_internal_diameter(nominal_diameter = d)
                d_m = _to_value(d)
                if d_m is not None and d_m >= D_initial:
                    selected_diameter_obj = d
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
        # The calculation used the internal diameter of the selected size; the
        # nominal size was reported in its place.
        internal_final = final_pipe_object.internal_diameter or D_final
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
                "calculated_diameter_m": internal_final.to("m").value,
                "nominal_diameter": D_final,
                "available_dp_met": available_dp_met,
            },
            "components": [
                {
                    "type": "pipe",
                    "name": pipe.name,
                    "length": pipe.length,
                    "diameter": internal_final,
                    "nominal_diameter": D_final,
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
    
        pipes = network.get_all_pipes() if hasattr(network, "get_all_pipes") else \
            [p for branch in self._normalize_branches(network) for p in branch if isinstance(p, Pipe)]

        for pipe in pipes:
            flow_rate = getattr(pipe, "flow_rate", None) or self._infer_flowrate()
            if flow_rate is None or float(getattr(flow_rate, "value", flow_rate)) <= 0:
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
    
            # Standard sizes are nominal; the hydraulics need the internal diameter
            # for that nominal size and schedule.
            schedule = getattr(pipe, "schedule", "STD") or "STD"

            def _internal(nominal):
                return get_internal_diameter(nominal, schedule) or nominal

            std_diams = list_available_pipe_diameters()
            D_candidates = []
            for idx, d in enumerate(std_diams):
                if _internal(d).to("m").value >= D_initial:
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
                id_test = _internal(D_test)
                pipe.internal_diameter = id_test
                calc = self._pipe_calculation(pipe, flow_rate)
                results_list.append({
                    "nominal_diameter": D_test,
                    "diameter": id_test,
                    "diameter_m": id_test.to("m").value,
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
                    print(f"  {r['nominal_diameter'].to('in')} -> {r['velocity_m_s']:.2f} m/s, {r['pressure_drop_Pa']:.2f} Pa")
                best_result = results_list[len(results_list)//2]
    
            pipe.nominal_diameter = best_result["nominal_diameter"]
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
                    "nominal_diameter": best_result["nominal_diameter"],
                },
                "components": [{
                    "type": "pipe",
                    "name": pipe.name,
                    "length": pipe.length,
                    "diameter": best_result["diameter"],
                    "nominal_diameter": best_result["nominal_diameter"],
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

