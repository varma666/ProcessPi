from ..base import CalculationBase
from ...units import *

class HeatExchangerArea(CalculationBase):
    """
    Calculate required heat exchanger area.
    Formula:
        Q = U * A * ΔTlm
        => A = Q / (U * ΔTlm)
    """

    def validate_inputs(self):
        required = ["heat_duty", "overall_heat_transfer_coeff", "log_mean_temp_diff"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")
        if self.inputs["log_mean_temp_diff"] <= 0:
            raise ValueError("Log mean temperature difference must be positive")

    def calculate(self):
        Q = self._get_value(self.inputs["heat_duty"], "heat_duty")  # W
        U = self._get_value(self.inputs["overall_heat_transfer_coeff"], "overall_heat_transfer_coeff")  # W/m²·K
        ΔTlm = self._get_value(self.inputs["log_mean_temp_diff"], "log_mean_temp_diff")  # K

        A = Q / (U * ΔTlm)
        return Area(A, "m2")
