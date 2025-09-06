from ..base import CalculationBase
from ...units import *

class NusseltNumber(CalculationBase):
    """
    Nusselt number (dimensionless heat transfer coefficient).

    **Formula:**
        Nu = h * L / k
    """
    def validate_inputs(self):
        required = ["h", "L", "k"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        h = self._get_value(self.inputs["h"], "heat_transfer_coefficient")
        L = self._get_value(self.inputs["L"], "length")
        k = self._get_value(self.inputs["k"], "thermal_conductivity")
        return Dimensionless(h * L / k)
