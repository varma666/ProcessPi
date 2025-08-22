from typing import Optional, Dict, Union
from .base import PipelineBase
from ..units import Power, Pressure
from .standards import PUMP_EFFICIENCIES


class Pump(PipelineBase):
    """
    Represents a pump in a pipeline system.

    Attributes:
        pump_type (str): Type of pump (e.g., 'centrifugal', 'positive_displacement').
        flow_rate (float): Volumetric flow rate (m³/s).
        head (float): Pump head (m), calculated automatically from pressures if provided.
        density (float): Fluid density (kg/m³). Default = 1000 (water).
        efficiency (float): Pump efficiency (0 < η ≤ 1). Loaded from standards if available.
        inlet_pressure (Pressure): Inlet pressure to the pump.
        outlet_pressure (Pressure): Outlet pressure from the pump.
    """

    def __init__(
        self,
        pump_type: str,
        flow_rate: float,
        head: Optional[float] = None,
        density: float = 1000,
        efficiency: Optional[float] = None,
        inlet_pressure: Optional[Pressure] = None,
        outlet_pressure: Optional[Pressure] = None,
    ):
        self.pump_type = pump_type
        self.flow_rate = flow_rate
        self.density = density
        self.inlet_pressure = inlet_pressure
        self.outlet_pressure = outlet_pressure

        # Calculate head from pressure difference if available
        if outlet_pressure and inlet_pressure:
            dp_pa = (outlet_pressure.to("Pa").value - inlet_pressure.to("Pa").value)
            self.head = dp_pa / (density * 9.81)
        else:
            self.head = head or 0.0  # Default head to 0 if neither pressures nor head provided

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
        return self.hydraulic_power() / self.efficiency if self.efficiency > 0 else 0.0

    def to_dict(self) -> Dict[str, Union[str, float]]:
        """
        Export pump properties and calculations as a dictionary.
        """
        return {
            "pump_type": self.pump_type,
            "flow_rate_m3s": self.flow_rate,
            "density_kgm3": self.density,
            "efficiency": self.efficiency,
            "head_m": self.head,
            "hydraulic_power_W": self.hydraulic_power(),
            "brake_power_W": self.brake_power(),
            "inlet_pressure_Pa": self.inlet_pressure.to("Pa").value if self.inlet_pressure else None,
            "outlet_pressure_Pa": self.outlet_pressure.to("Pa").value if self.outlet_pressure else None,
        }

    def calculate(self):
        """
        Perform calculations and return results.
        """
        return self.to_dict()
