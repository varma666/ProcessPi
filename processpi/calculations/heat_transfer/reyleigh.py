from ..base import CalculationBase
from ...units import *

class RayleighNumber(CalculationBase):
    """
    Rayleigh number (convection onset parameter).

    **Formula:**
        Ra = Gr * Pr
    """
    def validate_inputs(self):
        required = ["Gr", "Pr"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        Gr = self._get_value(self.inputs["Gr"], "dimensionless")
        Pr = self._get_value(self.inputs["Pr"], "dimensionless")

        return Dimensionless(Gr * Pr)
