from ..base import CalculationBase
from ...units import *

class ConvectionHeatLoss(CalculationBase):
    """
    Calculate convection heat loss.
    Formula:
        Q = h * A * ΔT
    """

    def validate_inputs(self):
        required = ["heat_transfer_coeff", "area", "temp_difference"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        h = self._get_value(self.inputs["heat_transfer_coeff"], "heat_transfer_coeff")  # W/m²·K
        A = self._get_value(self.inputs["area"], "area")                                # m²
        ΔT = self._get_value(self.inputs["temp_difference"], "temp_difference")         # K

        Q = h * A * ΔT
        return HeatFlux(Q, "W")
