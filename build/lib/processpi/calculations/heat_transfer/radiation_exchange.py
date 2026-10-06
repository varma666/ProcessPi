from ..base import CalculationBase
from ...units import *

class RadiationExchange(CalculationBase):
    """
    Net radiative heat exchange between two diffuse gray surfaces.

    **Formula:**
        q = σ * (T1^4 – T2^4) / ( (1/ε1) + (1/ε2) – 1 )

    **Where:**
        * T1, T2 = absolute temperatures [K]
        * ε1, ε2 = emissivities
        * q = net flux [W/m²]

    **Inputs:**
        * T1
        * T2
        * epsilon1
        * epsilon2

    **Output:**
        * HeatFlux [W/m²]
    """

    def validate_inputs(self):
        required = ["T1", "T2", "epsilon1", "epsilon2"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        sigma = 5.670374419e-8
        T1 = self._get_value(self.inputs["T1"], "temperature")
        T2 = self._get_value(self.inputs["T2"], "temperature")
        e1 = self.inputs["epsilon1"]
        e2 = self.inputs["epsilon2"]

        denominator = (1/e1) + (1/e2) - 1
        q = sigma * (T1**4 - T2**4) / denominator
        return HeatFlux(q)
