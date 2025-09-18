# processpi/equipment/pumps.py
from typing import Optional, Dict, Any
from ..units import Pressure, Length, Power
from ..streams import MaterialStream
from .base import Equipment
from ..pipelines.standards import PUMP_EFFICIENCIES


class Pump(Equipment):
    def __init__(self, name: str, pump_type: str,
                 efficiency: Optional[float] = None):
        super().__init__(name, inlet_ports=1, outlet_ports=1)
        self.pump_type = pump_type
        self.efficiency = efficiency or PUMP_EFFICIENCIES.get(pump_type, 0.7)

    def calculate(self) -> Dict[str, Any]:
        """
        Uses attached MaterialStreams to calculate head, power, etc.
        """
        inlet: MaterialStream = self.inlets[0]
        outlet: MaterialStream = self.outlets[0]

        if inlet is None or outlet is None:
            raise ValueError("Pump must have both inlet and outlet streams connected")

        if inlet.density is None or inlet.flow_rate is None:
            raise ValueError("Inlet stream must have density and flow_rate defined")

        # Pressure rise
        dp = outlet.pressure.to("Pa").value - inlet.pressure.to("Pa").value
        rho = inlet.rho
        head_m = dp / (rho * 9.81)

        # Hydraulic and brake power
        flow_rate = inlet.volumetric_flow
        hydraulic_power = rho * 9.81 * flow_rate * head_m
        brake_power = hydraulic_power / self.efficiency if self.efficiency > 0 else float("inf")

        return {
            "head": Length(head_m, "m"),
            "hydraulic_power": Power(hydraulic_power, "W"),
            "brake_power": Power(brake_power, "W"),
            "efficiency": self.efficiency,
        }
