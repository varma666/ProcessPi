from ..base import CalculationBase
from ...units import *

class BiotNumber(CalculationBase):
    """
    Biot number.

    **Formula:**
        Bi = h * Lc / k
    """
    def validate_inputs(self):
        required = ["h", "Lc", "k"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        h = self._get_value(self.inputs["h"], "heat_transfer_coefficient")
        Lc = self._get_value(self.inputs["Lc"], "length")
        k = self._get_value(self.inputs["k"], "thermal_conductivity")
        return Dimensionless(h * Lc / k)
