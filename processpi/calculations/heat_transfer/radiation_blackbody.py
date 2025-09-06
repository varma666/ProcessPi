from ..base import CalculationBase
from ...units import *

class BlackbodyRadiation(CalculationBase):
    """
    Stefan–Boltzmann law for blackbody radiation.

    **Formula:**
        q = σ * T^4

    **Where:**
        * q = radiative flux [W/m²]
        * σ = Stefan–Boltzmann constant (5.670374419e-8 W/m²·K⁴)
        * T = absolute temperature [K]

    **Inputs:**
        * T  – surface temperature [K]

    **Output:**
        * HeatFlux [W/m²]
    """

    def validate_inputs(self):
        if "T" not in self.inputs:
            raise ValueError("Missing required input: T")

    def calculate(self):
        sigma = 5.670374419e-8  # Stefan–Boltzmann constant
        T = self._get_value(self.inputs["T"], "temperature")
        q = sigma * T**4
        return HeatFlux(q)
