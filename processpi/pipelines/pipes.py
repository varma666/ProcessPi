# processpi/pipelines/pipes.py

from typing import Optional, Dict, Any
from .base import PipelineBase
from ..units import Diameter, Length, Pressure, UnitfulValue
from .standards import get_roughness, get_internal_diameter


class Pipe(PipelineBase):
    """
    Represents a straight section of a process pipeline.

    This class encapsulates the physical properties necessary for fluid flow
    calculations, including its geometry (diameter, length) and material
    properties (roughness). It can also store a state (e.g., inlet/outlet pressure)
    from a solved simulation.

    Attributes:
        nominal_diameter (Optional[Diameter]): The nominal diameter of the pipe.
        schedule (str): The pipe schedule (e.g., '40', '80', 'STD', 'XS').
        material (str): The material of construction (e.g., 'CS' for Carbon Steel).
        length (Length): The length of the pipe section.
        roughness (UnitfulValue): The absolute roughness of the pipe's internal
                                  surface, in meters.
        internal_diameter (Optional[UnitfulValue]): The actual internal diameter of the pipe.
        inlet_pressure (Optional[Pressure]): The pressure at the pipe's inlet.
        outlet_pressure (Optional[Pressure]): The pressure at the pipe's outlet.
        start_node (Optional[Any]): The node object connected to the pipe's inlet.
        end_node (Optional[Any]): The node object connected to the pipe's outlet.
        is_optimization_target (bool): A flag to indicate if this pipe's diameter
                                       is a variable to be optimized.
    """

    def __init__(
        self,
        name: str,
        nominal_diameter: Optional[Diameter] = None,
        schedule: str = "40",
        material: str = "CS",
        length: Optional[Length] = None,
        inlet_pressure: Optional[Pressure] = None,
        outlet_pressure: Optional[Pressure] = None,
        internal_diameter: Optional[Diameter] = None,
    ):
        """
        Initializes a Pipe instance.

        Args:
            name (str): A unique name for the pipe.
            nominal_diameter (Optional[Diameter]): Nominal pipe size. If `None`,
                                                   this pipe is a candidate for
                                                   optimization.
            schedule (str, optional): Pipe schedule. Defaults to "40".
            material (str, optional): Pipe material. Defaults to "CS".
            length (Optional[Length], optional): Pipe length. Defaults to 1 meter.
            inlet_pressure (Optional[Pressure], optional): Explicitly set inlet pressure.
            outlet_pressure (Optional[Pressure], optional): Explicitly set outlet pressure.
            internal_diameter (Optional[Diameter], optional): Explicitly set internal
                                                              diameter. Overrides lookup.
        """
        super().__init__(name)

        # Flag for the optimization engine
        self.is_optimization_target: bool = (nominal_diameter is None and internal_diameter is None)
        
        self.nominal_diameter: Optional[Diameter] = nominal_diameter
        self.schedule: str = schedule
        self.material: str = material
        self.length: Length = length or Length(1.0, "m")
        
        # Load properties from standards database.
        self.roughness: UnitfulValue = get_roughness(self.material)
        self.internal_diameter: Optional[UnitfulValue] = None
        
        # Set the initial internal diameter if provided.
        if internal_diameter:
            self.internal_diameter = internal_diameter
        elif nominal_diameter:
            self.internal_diameter = get_internal_diameter(self.nominal_diameter, self.schedule)

        # Optional user-defined pressures.
        self.inlet_pressure: Optional[Pressure] = inlet_pressure
        self.outlet_pressure: Optional[Pressure] = outlet_pressure
        
        # Node connections (set by the network builder)
        self.start_node: Optional[Any] = None
        self.end_node: Optional[Any] = None
        
    def cross_sectional_area(self) -> Optional[UnitfulValue]:
        """
        Calculates the cross-sectional flow area of the pipe.

        Returns:
            Optional[UnitfulValue]: The area in meters squared (m²), or None
                                    if the internal diameter is not set.
        """
        if self.internal_diameter is None:
            return None
        d_m = self.internal_diameter.to("m").value
        area_m2 = (3.14159 / 4) * (d_m**2)
        return UnitfulValue(area_m2, "m²")

    def surface_area(self) -> Optional[UnitfulValue]:
        """
        Calculates the external surface area of the pipe.

        Returns:
            Optional[UnitfulValue]: The surface area in meters squared (m²),
                                    or None if the nominal diameter is not set.
        """
        if self.nominal_diameter is None:
            return None
        d_m = self.nominal_diameter.to("m").value
        area_m2 = 3.14159 * d_m * self.length.to("m").value
        return UnitfulValue(area_m2, "m²")

    def pressure_difference(self) -> Optional[Pressure]:
        """
        Calculates the pressure drop or gain across the pipe if both inlet and
        outlet pressures are defined.

        Returns:
            Optional[Pressure]: The pressure difference as a `Pressure` object,
                                or `None` if data is incomplete.
        """
        if self.inlet_pressure and self.outlet_pressure:
            return self.inlet_pressure - self.outlet_pressure
        return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Exports all relevant pipe properties as a dictionary for logging and
        reporting purposes.
        """
        return {
            "name": self.name,
            "nominal_diameter": self.nominal_diameter.to_dict() if self.nominal_diameter else None,
            "is_optimization_target": self.is_optimization_target,
            "schedule": self.schedule,
            "material": self.material,
            "length": self.length.to_dict(),
            "roughness": self.roughness.to_dict(),
            "internal_diameter": self.internal_diameter.to_dict() if self.internal_diameter else None,
            "cross_sectional_area": self.cross_sectional_area().to_dict() if self.cross_sectional_area() else None,
            "inlet_pressure": self.inlet_pressure.to_dict() if self.inlet_pressure else None,
            "outlet_pressure": self.outlet_pressure.to_dict() if self.outlet_pressure else None,
            "pressure_difference": self.pressure_difference().to_dict() if self.pressure_difference() else None,
        }

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the object."""
        dia_repr = f"nominal_diameter={self.nominal_diameter}" if self.nominal_diameter else "OPTIMIZE"
        return (
            f"Pipe(name='{self.name}', {dia_repr}, "
            f"schedule='{self.schedule}', length={self.length})"
        )
    
    def calculate(self):
        """
        Placeholder method for pipe-specific calculations.
        The actual flow calculation logic is handled by the `PipelineEngine`.
        """
        return self.to_dict()
