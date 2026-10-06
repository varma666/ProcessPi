from ..base import CalculationBase
from ...units import *

class NTUHeatExchanger(CalculationBase):
    """
    Heat Exchanger using Effectiveness-NTU method.
    Q = ε * C_min * (T_hot,in - T_cold,in)
    """
    def validate_inputs(self):
        required = ["effectiveness", "C_min", "T_hot_in", "T_cold_in"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        eps = self._get_value(self.inputs["effectiveness"], "dimensionless")
        C_min = self._get_value(self.inputs["C_min"], "heat_capacity_rate")  # W/K
        Th_in = self._get_value(self.inputs["T_hot_in"], "temperature")
        Tc_in = self._get_value(self.inputs["T_cold_in"], "temperature")

        return HeatFlow(eps * C_min * (Th_in - Tc_in))
