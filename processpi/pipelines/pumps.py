from typing import Optional, Dict, Union
from .base import PipelineBase
from ..units import Power
from .standards import PUMP_EFFICIENCIES

class Pump(PipelineBase):
    """
    Represents a pump in a pipeline system.

    Attributes:
        pump_type (str): Type of pump (e.g., 'centrifugal', 'positive_displacement').
        flow_rate (float): Volumetric flow rate (m³/s).
        head (float): Pump head (m).
        density (float): Fluid density (kg/m³). Default = 1000 (water).
        efficiency (float): Pump efficiency (0 < η ≤ 1). 
                            Loaded from standards if available.
    """

    def __init__(
        self,
        pump_type: str,
        flow_rate: float,
        head: float,
        density: float = 1000,
        efficiency: Optional[float] = None,
    ):
        self.pump_type = pump_type
        self.flow_rate = flow_rate
        self.head = head
        self.density = density
        self.efficiency = efficiency or PUMP_EFFICIENCIES.get(pump_type, 0.7)

    def hydraulic_power(self) -> float:
        """
        Calculate the hydraulic power required by the pump.

        Formula:
            P_h = ρ * g * Q * H   (W)
        """
        g = 9.81  # m/s²
        return self.density * g * self.flow_rate * self.head

    def brake_power(self) -> float:
        """
        Calculate the brake power required considering efficiency.

        Formula:
            P_b = P_h / η   (W)
        """
        return self.hydraulic_power() / self.efficiency

    def to_dict(self) -> Dict[str, Union[str, float]]:
        """
        Export pump properties and calculations as a dictionary.
        """
        return {
            "pump_type": self.pump_type,
            "flow_rate_m3s": self.flow_rate,
            "head_m": self.head,
            "density_kgm3": self.density,
            "efficiency": self.efficiency,
            "hydraulic_power_W": self.hydraulic_power(),
            "brake_power_W": self.brake_power(),
        }

    def calculate(self):
        """
        Perform calculations and return results.
        """
        return self.to_dict()
