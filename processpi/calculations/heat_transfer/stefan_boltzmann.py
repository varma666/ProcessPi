from ..base import CalculationBase
from ...units import *

# Stefan–Boltzmann constant
SIGMA = 5.670374419e-8  # W/m²·K⁴

class StefanBoltzmann(CalculationBase):
    """
    Radiative heat transfer (Stefan–Boltzmann Law).

    **Formula:**
        q = εσA(Ts⁴ - Tsur⁴)

    **Where:**
        * ε    = Surface emissivity [-]
        * σ    = Stefan–Boltzmann constant [5.67e-8 W/m²·K⁴]
        * A    = Surface area [m²]
        * Ts   = Surface temperature [K]
        * Tsur = Surrounding temperature [K]

    **Inputs:**
        * `emissivity`: Surface emissivity.
        * `area`: Surface area.
        * `T_surface`: Surface temperature.
        * `T_surround`: Surrounding temperature.

    **Output:**
        * HeatFlow [W]
    """

    def validate_inputs(self):
        required = ["emissivity", "area", "T_surface", "T_surround"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        eps = self._get_value(self.inputs["emissivity"], "dimensionless")
        A = self._get_value(self.inputs["area"], "area")                       # m²
        Ts = self._get_value(self.inputs["T_surface"], "temperature")          # K
        Tsur = self._get_value(self.inputs["T_surround"], "temperature")       # K

        q = eps * SIGMA * A * (Ts**4 - Tsur**4)  # W
        return HeatFlow(q)
