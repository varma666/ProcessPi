# processpi/pipelines/pipes.py

from typing import Optional, Dict
from .base import PipelineBase
from ..units import *
from .standards import get_roughness, get_internal_diameter


class Pipe(PipelineBase):
    """
    Represents a process pipeline element with geometric and material properties.

    Attributes:
        nominal_diameter (Diameter): Nominal diameter of the pipe (mm or inch).
        schedule (str): Pipe schedule (e.g., '40', '80', 'STD', 'XS').
        material (str): Pipe material (e.g., 'CS', 'SS316', 'PVC').
        length (Length): Length of the pipe.
        roughness (float): Absolute roughness of the pipe (mm).
        internal_diameter (Diameter): Internal diameter based on nominal diameter and schedule.
        inlet_pressure (Pressure): Optional inlet pressure for the pipe.
        outlet_pressure (Pressure): Optional outlet pressure for the pipe.
    """

    def __init__(
        self,
        nominal_diameter: Diameter,
        schedule: str = "40",
        material: str = "CS",
        length: Optional[Length] = None,
        inlet_pressure: Optional[Pressure] = None,
        outlet_pressure: Optional[Pressure] = None,
    ):
        self.nominal_diameter = nominal_diameter
        self.schedule = schedule
        self.material = material
        self.length = length or Length(1.0, "m")  # default 1 meter
        self.roughness = get_roughness(self.material)
        self.internal_diameter = get_internal_diameter(self.nominal_diameter, self.schedule)
        self.inlet_pressure = inlet_pressure  # user can set this explicitly
        self.outlet_pressure = outlet_pressure  # user can set this explicitly

    def cross_sectional_area(self) -> float:
        """
        Calculate cross-sectional flow area (m²).
        """
        d_m = self.internal_diameter.to("m").value
        return 3.14159 * (d_m / 2) ** 2

    def surface_area(self) -> float:
        """
        Calculate external surface area (m²) for heat loss calculations.
        """
        d_m = self.nominal_diameter.to("m").value
        return 3.14159 * d_m * self.length.to("m").value

    def pressure_difference(self) -> Optional[Pressure]:
        """
        Calculate the pressure difference (inlet - outlet) if both are defined.
        """
        if self.inlet_pressure and self.outlet_pressure:
            return self.inlet_pressure - self.outlet_pressure
        return None

    def to_dict(self) -> Dict[str, Optional[float]]:
        """
        Export pipe properties as dictionary for reporting.
        """
        return {
            "nominal_diameter_mm": self.nominal_diameter.value,
            "schedule": self.schedule,
            "material": self.material,
            "length_m": self.length.to("m").value,
            "roughness_mm": self.roughness,
            "internal_diameter_mm": self.internal_diameter.value if self.internal_diameter else None,
            "inlet_pressure_Pa": self.inlet_pressure.to("Pa").value if self.inlet_pressure else None,
            "outlet_pressure_Pa": self.outlet_pressure.to("Pa").value if self.outlet_pressure else None,
            "pressure_difference_Pa": self.pressure_difference().to("Pa").value if self.pressure_difference() else None,
        }

    def calculate(self):
        """
        Placeholder for pipe-specific calculations.
        """
        pass
