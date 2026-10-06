from ..base import CalculationBase
from ...units import *

class RadiationWithViewFactor(CalculationBase):
    """
    Radiation exchange between two surfaces with a given view factor.

    **Formula:**
        Q = σ * A1 * F12 * (T1^4 – T2^4)

    **Where:**
        * A1 = area of surface 1 [m²]
        * F12 = view factor from surface 1 to 2
        * T1, T2 = temperatures [K]
        * Q = net heat transfer [W]

    **Inputs:**
        * A1
        * F12
        * T1
        * T2

    **Output:**
        * HeatFlow [W]
    """

    def validate_inputs(self):
        required = ["A1", "F12", "T1", "T2"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        sigma = 5.670374419e-8
        A1 = self._get_value(self.inputs["A1"], "area")
        F12 = self.inputs["F12"]
        T1 = self._get_value(self.inputs["T1"], "temperature")
        T2 = self._get_value(self.inputs["T2"], "temperature")

        Q = sigma * A1 * F12 * (T1**4 - T2**4)
        return HeatFlow(Q)
