# processpi/pipelines/pipes.py

from typing import Optional, Dict
from .base import PipelineBase
from ..units import *
from .standards import *


class Pipe(PipelineBase):
    """
    Represents a process pipeline element with geometric and material properties.
    
    Attributes:
        nominal_diameter (float): Nominal diameter of the pipe (mm or inch).
        schedule (str): Pipe schedule (e.g., '40', '80', 'STD', 'XS').
        material (str): Pipe material (e.g., 'CS', 'SS316', 'PVC').
        length (float): Length of the pipe (m).
        roughness (float): Absolute roughness of the pipe (mm).
        insulation_thickness (float): Thickness of insulation (mm).
        insulation_material (str): Material used for insulation.
    """

    def __init__(
        self,
        nominal_diameter: Diameter,
        schedule: str,
        material: str,
        length: Length,
        
    ):
        self.nominal_diameter = nominal_diameter
        self.schedule = schedule
        self.material = material
        self.length = length
        self.roughness = get_roughness(self.material)

    def cross_sectional_area(self) -> float:
        """
        Calculate cross-sectional flow area (m²).
        """
        d = self.internal_diameter() / 1000  # convert mm → m
        return 3.14159 * (d / 2) ** 2

    def surface_area(self) -> float:
        """
        Calculate external surface area (m²) for heat loss calculations.
        """
        d = self.nominal_diameter / 1000  # mm → m
        return 3.14159 * d * self.length

    def to_dict(self) -> Dict[str, Optional[float]]:
        """
        Export pipe properties as dictionary for reporting.
        """
        return {
            "nominal_diameter_mm": self.nominal_diameter,
            "schedule": self.schedule,
            "material": self.material,
            "length_m": self.length,
            "roughness_mm": self.roughness,
            "internal_diameter_mm": self.internal_diameter(),
            "insulation_thickness_mm": self.insulation_thickness,
            "insulation_material": self.insulation_material,
        }
