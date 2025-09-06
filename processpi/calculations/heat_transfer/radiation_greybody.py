from ..base import CalculationBase
from ...units import *

class GraybodyRadiation(CalculationBase):
    """
    Graybody radiation with emissivity factor.

    **Formula:**
        q = ε * σ * T^4

    **Where:**
        * ε = emissivity (0 < ε ≤ 1)
        * q = radiative flux [W/m²]
        * T = absolute temperature [K]

    **Inputs:**
        * T  – surface temperature [K]
        * ε  – emissivity (dimensionless)

    **Output:**
        * HeatFlux [W/m²]
    """

    def validate_inputs(self):
        required = ["T", "epsilon"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        sigma = 5.670374419e-8
        T = self._get_value(self.inputs["T"], "temperature")
        epsilon = self.inputs["epsilon"]
        q = epsilon * sigma * T**4
        return HeatFlux(q)
