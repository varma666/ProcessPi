from ..base import CalculationBase
from ...units import *

class FourierLaw(CalculationBase):
    """
    Heat transfer rate by conduction (Fourier's Law).

    **Formula:**
        q = k * A * (ΔT / dx)

    **Where:**
        * k   = Thermal conductivity [W/m·K]
        * A   = Cross-sectional area [m²]
        * ΔT  = Temperature difference [K]
        * dx  = Thickness of material [m]

    **Inputs:**
        * `conductivity`: Thermal conductivity (k).
        * `area`: Heat transfer area (A).
        * `deltaT`: Temperature difference (ΔT).
        * `thickness`: Material thickness (dx).

    **Output:**
        * HeatFlow [W]
    """

    def validate_inputs(self):
        required = ["conductivity", "area", "deltaT", "thickness"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        k = self._get_value(self.inputs["conductivity"], "conductivity")  # W/m·K
        A = self._get_value(self.inputs["area"], "area")                  # m²
        dT = self._get_value(self.inputs["deltaT"], "temperature")        # K
        dx = self._get_value(self.inputs["thickness"], "length")          # m

        q = k * A * (dT / dx)  # W
        return HeatFlow(q)  # return in Watts
