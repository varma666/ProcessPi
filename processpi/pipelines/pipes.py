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
        nominal_diameter (Optional[Diameter]): The nominal diameter of the pipe. This
                                               is a standard size used for designation.
        schedule (str): The pipe schedule (e.g., '40', '80', 'STD', 'XS'), which
                        defines the wall thickness and thus the internal diameter.
        material (str): The material of construction (e.g., 'CS' for Carbon Steel).
                        Used to look up standard roughness values.
        length (Length): The length of the pipe section.
        roughness (UnitfulValue): The absolute roughness of the pipe's internal
                                  surface, in meters. It is a key factor in
                                  calculating the friction factor.
        internal_diameter (UnitfulValue): The actual internal diameter of the pipe,
                                          calculated based on the nominal diameter and schedule.
        inlet_pressure (Optional[Pressure]): The pressure at the pipe's inlet.
        outlet_pressure (Optional[Pressure]): The pressure at the pipe's outlet.
        start_node (Optional[Any]): The node object connected to the pipe's inlet.
        end_node (Optional[Any]): The node object connected to the pipe's outlet.
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
            nominal_diameter (Optional[Diameter]): Nominal pipe size. Required if
                                                   `internal_diameter` is not provided.
            schedule (str, optional): Pipe schedule. Defaults to "40".
            material (str, optional): Pipe material. Defaults to "CS".
            length (Optional[Length], optional): Pipe length. Defaults to 1 meter.
            inlet_pressure (Optional[Pressure], optional): Explicitly set inlet pressure.
            outlet_pressure (Optional[Pressure], optional): Explicitly set outlet pressure.
            internal_diameter (Optional[Diameter], optional): Explicitly set internal
                                                              diameter. Overrides lookup.
        
        Raises:
            ValueError: If neither nominal diameter nor internal diameter is provided.
        """
        # Ensure at least one way to define diameter is provided.
        if nominal_diameter is None and internal_diameter is None:
            raise ValueError("Either `nominal_diameter` or `internal_diameter` must be provided.")
        
        # Call the parent class's constructor
        super().__init__(name)

        self.nominal_diameter: Optional[Diameter] = nominal_diameter
        self.schedule: str = schedule
        self.material: str = material
        self.length: Length = length or Length(1.0, "m")
        
        # Load properties from standards database.
        self.roughness: UnitfulValue = get_roughness(self.material)
        if internal_diameter:
            self.internal_diameter: UnitfulValue = internal_diameter
        else:
            self.internal_diameter: UnitfulValue = get_internal_diameter(self.nominal_diameter, self.schedule)
            
        # Optional user-defined pressures.
        self.inlet_pressure: Optional[Pressure] = inlet_pressure
        self.outlet_pressure: Optional[Pressure] = outlet_pressure
        
        # Node connections (set by the network builder)
        self.start_node: Optional[Any] = None
        self.end_node: Optional[Any] = None

    def cross_sectional_area(self) -> UnitfulValue:
        """
        Calculates the cross-sectional flow area of the pipe.

        Returns:
            UnitfulValue: The area in meters squared ($m^2$).
        """
        d_m = self.internal_diameter.to("m").value
        area_m2 = (3.14159 / 4) * (d_m**2)
        return UnitfulValue(area_m2, "m²")

    def surface_area(self) -> UnitfulValue:
        """
        Calculates the external surface area of the pipe. This is primarily
        used for heat transfer calculations.

        Returns:
            UnitfulValue: The surface area in meters squared ($m^2$).
        """
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

        Returns:
            Dict[str, Any]: A dictionary of pipe attributes. `UnitfulValue`
                            objects are converted to dictionaries containing
                            their value and unit.
        """
        return {
            "name": self.name,
            "nominal_diameter": self.nominal_diameter.to_dict() if self.nominal_diameter else None,
            "schedule": self.schedule,
            "material": self.material,
            "length": self.length.to_dict(),
            "roughness": self.roughness.to_dict(),
            "internal_diameter": self.internal_diameter.to_dict(),
            "cross_sectional_area": self.cross_sectional_area().to_dict(),
            "inlet_pressure": self.inlet_pressure.to_dict() if self.inlet_pressure else None,
            "outlet_pressure": self.outlet_pressure.to_dict() if self.outlet_pressure else None,
            "pressure_difference": self.pressure_difference().to_dict() if self.pressure_difference() else None,
        }

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the object."""
        return (
            f"Pipe(name='{self.name}', nominal_diameter={self.nominal_diameter}, "
            f"schedule='{self.schedule}', length={self.length})"
        )

    def calculate(self):
        """
        Placeholder method for pipe-specific calculations.
        The actual flow calculation logic is handled by the `PipelineEngine`.
        """
        return self.to_dict()
