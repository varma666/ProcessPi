# processpi/pipelines/pipes.py

from typing import Optional, Dict, Any
from .base import PipelineBase
from ..units import *
from .standards import get_roughness, get_internal_diameter


class Pipe(PipelineBase):
    """
    Represents a straight section of a process pipeline.

    Encapsulates geometry (diameter, length), material properties (roughness),
    and state (inlet/outlet pressure). Useful for flow and pressure drop
    calculations, and compatible with optimization workflows.
    """

    def __init__(
        self,
        name: str,
        nominal_diameter: Optional[Diameter] = None,
        schedule: str = "STD",
        material: str = "CS",
        length: Optional[Length] = None,
        inlet_pressure: Optional[Pressure] = None,
        outlet_pressure: Optional[Pressure] = None,
        internal_diameter: Optional[Diameter] = None,
        flow_rate: Optional[VolumetricFlowRate] = None,  # <-- NEW
        **kwargs: Any
    ):
        """
        Initialize a Pipe instance.

        Args:
            name (str): Unique name of the pipe.
            nominal_diameter (Optional[Diameter]): Nominal pipe size. If `None`,
                this pipe is a candidate for optimization.
            schedule (str, optional): Pipe schedule. Defaults to "STD".
            material (str, optional): Pipe material. Defaults to "CS".
            length (Optional[Length], optional): Pipe length (default 1 meter).
            inlet_pressure (Optional[Pressure], optional): Inlet pressure.
            outlet_pressure (Optional[Pressure], optional): Outlet pressure.
            internal_diameter (Optional[Diameter], optional): Overrides the
                calculated internal diameter if provided.
            flow_rate (Optional[VolumetricFlowRate], optional): Initial flow rate
                for solver. Defaults to 0.001 m³/s.
            **kwargs: Additional custom parameters to store in the base class.
        """
        super().__init__(name=name, **kwargs)

        # Optimization flag
        self.is_optimization_target: bool = (
            nominal_diameter is None and internal_diameter is None
        )

        # Core attributes
        self.nominal_diameter: Optional[Diameter] = nominal_diameter
        self.schedule: str = schedule
        self.material: str = material
        self.length: Length = length or Length(1.0, "m")

        # Physical properties from standards
        self.roughness: Variable = get_roughness(self.material)
        self.internal_diameter: Optional[Variable] = None

        if internal_diameter:
            self.internal_diameter = internal_diameter
            #self.nominal_diameter = internal_diameter + ( 2 * get_thickness(internal_diameter, self.schedule))
        elif nominal_diameter:
            self.internal_diameter = get_internal_diameter(
                self.nominal_diameter, self.schedule
            )

        # Optional pressures
        self.inlet_pressure: Optional[Pressure] = inlet_pressure
        self.outlet_pressure: Optional[Pressure] = outlet_pressure

        # Nodes (set externally in network)
        self.start_node: Optional[Any] = None
        self.end_node: Optional[Any] = None

        # -----------------------------
        # NEW: flow_rate for solver initialization
        # -----------------------------
        self.flow_rate: VolumetricFlowRate = flow_rate or VolumetricFlowRate(0.001, "m3/s")

    # -------------------------------------------------------------------------
    # Derived calculations
    # -------------------------------------------------------------------------
    def cross_sectional_area(self) -> Optional[Variable]:
        """Calculate internal cross-sectional area (m²)."""
        if self.internal_diameter is None:
            return None
        d_m = self.internal_diameter.to("m").value
        area_m2 = (3.14159 / 4) * (d_m**2)
        return Variable(area_m2, "m²")

    def surface_area(self) -> Optional[Variable]:
        """Calculate external surface area (m²)."""
        if self.nominal_diameter is None:
            return None
        d_m = self.nominal_diameter.to("m").value
        area_m2 = 3.14159 * d_m * self.length.to("m").value
        return Variable(area_m2, "m²")

    def pressure_difference(self) -> Optional[Pressure]:
        """Calculate ΔP (inlet - outlet)."""
        if self.inlet_pressure and self.outlet_pressure:
            return self.inlet_pressure - self.outlet_pressure
        return None

    # -------------------------------------------------------------------------
    # Export and representation
    # -------------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Export all key pipe data as a dictionary."""
        return {
            "name": self.name,
            "nominal_diameter": self.nominal_diameter.to_dict()
            if self.nominal_diameter
            else None,
            "is_optimization_target": self.is_optimization_target,
            "schedule": self.schedule,
            "material": self.material,
            "length": self.length.to_dict(),
            "roughness": self.roughness.to_dict(),
            "internal_diameter": self.internal_diameter.to_dict()
            if self.internal_diameter
            else None,
            "cross_sectional_area": self.cross_sectional_area().to_dict()
            if self.cross_sectional_area()
            else None,
            "flow_rate": self.flow_rate.to_dict() if self.flow_rate else None,  # <-- NEW
            "inlet_pressure": self.inlet_pressure.to_dict()
            if self.inlet_pressure
            else None,
            "outlet_pressure": self.outlet_pressure.to_dict()
            if self.outlet_pressure
            else None,
            "pressure_difference": self.pressure_difference().to_dict()
            if self.pressure_difference()
            else None,
        }

    def __repr__(self) -> str:
        dia_repr = (
            f"nominal_diameter={self.nominal_diameter}"
            if self.nominal_diameter
            else "OPTIMIZE"
        )
        return (
            f"Pipe(name='{self.name}', {dia_repr}, "
            f"schedule='{self.schedule}', length={self.length}, "
            f"flow_rate={self.flow_rate})"  # <-- UPDATED
        )

    # -------------------------------------------------------------------------
    # Compatibility hook for PipelineEngine
    # -------------------------------------------------------------------------
    def calculate(self):
        """Return pipe data (for engine compatibility)."""
        return self.to_dict()
