from typing import Dict, Any
from ..streams import MaterialStream
from .base import Equipment
from ..calculations.heat_transfer.heat_exchanger_area import HeatExchangerArea

class HeatExchanger(Equipment):
    def __init__(self, name: str, hx_type: str = "generic"):
        # Two inlets (hot, cold) and two outlets
        super().__init__(name, inlet_ports=2, outlet_ports=2)
        self.hx_type = hx_type

    def calculate_area(self, heat_duty, U, deltaT_lm):
        """
        Wrapper around HeatExchangerArea calculation.
        Inputs can be Unit objects or raw values with compatible units.
        """
        calc = HeatExchangerArea(
            heat_duty=heat_duty,
            overall_heat_transfer_coeff=U,
            log_mean_temp_diff=deltaT_lm,
        )
        return calc.calculate()
