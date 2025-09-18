from typing import Dict, Any
from ..units import Temperature
from ..streams import MaterialStream
from .base import Equipment
from ..calculations import heatexchanger as hx_calc

class HeatExchanger(Equipment):
    def __init__(self, name: str, hx_type: str = "generic"):
        # 2 inlets (hot, cold) and 2 outlets
        super().__init__(name, inlet_ports=2, outlet_ports=2)
        self.hx_type = hx_type

    def calculate(self) -> Dict[str, Any]:
        """
        Uses attached MaterialStreams to calculate energy balance.
        """
        hot_in, cold_in = self.inlets
        hot_out, cold_out = self.outlets

        if None in [hot_in, cold_in, hot_out, cold_out]:
            raise ValueError("All 4 streams (2 in, 2 out) must be connected")

        # Example: assume Cp given per stream for now
        if not hasattr(hot_in, "cp") or not hasattr(cold_in, "cp"):
            raise AttributeError("Streams must define cp (J/kg-K) for heat exchanger calculations")

        # Hot side
        dT_hot = hot_in.temperature.to("K").value - hot_out.temperature.to("K").value
        Q_hot = hx_calc.heat_duty(hot_in.mass_flow().to("kg/s").value,
                                  hot_in.cp, dT_hot)

        # Cold side
        dT_cold = cold_out.temperature.to("K").value - cold_in.temperature.to("K").value
        Q_cold = hx_calc.heat_duty(cold_in.mass_flow().to("kg/s").value,
                                   cold_in.cp, dT_cold)

        # Energy balance check
        imbalance = Q_hot.to("W").value - Q_cold.to("W").value

        return {
            "Q_hot": Q_hot,
            "Q_cold": Q_cold,
            "imbalance_W": imbalance
        }
