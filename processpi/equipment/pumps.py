# processpi/equipment/pumps.py
from typing import Optional, Dict, Any
from ..units import Pressure, Length, Power
from ..streams import MaterialStream, EnergyStream
from .base import Equipment
from ..pipelines.standards import PUMP_EFFICIENCIES


class Pump(Equipment):
    """
    Pump equipment unit.
    Simulates pressure rise, head, hydraulic power, and brake power
    based on inlet/outlet MaterialStreams.
    """

    def __init__(self, name: str, pump_type: str,
                 efficiency: Optional[float] = None):
        super().__init__(name, inlet_ports=1, outlet_ports=1)
        self.pump_type = pump_type
        self.efficiency: float = efficiency or PUMP_EFFICIENCIES.get(pump_type, 0.7)
        self.energy_stream: Optional[EnergyStream] = None  # logs brake power

    def simulate(self) -> Dict[str, Any]:
        """
        Uses attached MaterialStreams to calculate head, power, etc.
        Also attaches an EnergyStream to log brake power.
        """
        inlet: Optional[MaterialStream] = self.inlets[0]
        outlet: Optional[MaterialStream] = self.outlets[0]

        if inlet is None or outlet is None:
            raise ValueError(
                f"Pump {self.name}: must have both inlet and outlet streams connected"
            )

        if inlet.density is None or inlet.flow_rate is None:
            raise ValueError(
                f"Pump {self.name}: inlet stream must have density and flow_rate defined"
            )

        # --- Pressure rise (ΔP) ---
        dp = outlet.pressure.to("Pa").value - inlet.pressure.to("Pa").value
        rho = inlet.density()  # density unit expected to be mass/volume
        g = 9.81  # gravitational acceleration (m/s²)
        head_m = dp / (rho.value * g)

        # --- Power calculations ---
        flow_rate = inlet.flow_rate  # volumetric flow rate
        hydraulic_power = rho.value * g * flow_rate.value * head_m
        brake_power = (
            hydraulic_power / self.efficiency if self.efficiency > 0 else float("inf")
        )

        # --- Energy stream attachment ---
        self.energy_stream = EnergyStream(
            name=f"{self.name}_work_in",
            duty=Power(brake_power, "W")
        )

        return {
            "head": Length(head_m, "m"),
            "hydraulic_power": Power(hydraulic_power, "W"),
            "brake_power": Power(brake_power, "W"),
            "efficiency": self.efficiency,
            "energy_stream": self.energy_stream,
        }
