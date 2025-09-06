from ..base import CalculationBase
from ...units import *

class FourierNumber(CalculationBase):
    """
    Fourier number (transient conduction).

    **Formula:**
        Fo = α * t / L²
    """
    def validate_inputs(self):
        required = ["alpha", "time", "L"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        alpha = self._get_value(self.inputs["alpha"], "thermal_diffusivity")
        t     = self._get_value(self.inputs["time"], "time")
        L     = self._get_value(self.inputs["L"], "length")

        return Dimensionless(alpha * t / (L**2))
