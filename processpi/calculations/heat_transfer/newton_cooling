from ..base import CalculationBase
from ...units import *

class NewtonCooling(CalculationBase):
    """
    Convective heat transfer (Newton’s Law of Cooling).

    **Formula:**
        q = h * A * (Ts - T∞)

    **Where:**
        * h   = Heat transfer coefficient [W/m²·K]
        * A   = Surface area [m²]
        * Ts  = Surface temperature [K]
        * T∞  = Bulk fluid temperature [K]

    **Inputs:**
        * `h`: Heat transfer coefficient.
        * `area`: Surface area.
        * `T_surface`: Surface temperature.
        * `T_fluid`: Bulk fluid temperature.

    **Output:**
        * HeatFlow [W]
    """

    def validate_inputs(self):
        required = ["h", "area", "T_surface", "T_fluid"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        h = self._get_value(self.inputs["h"], "heat_transfer_coefficient")  # W/m²·K
        A = self._get_value(self.inputs["area"], "area")                    # m²
        Ts = self._get_value(self.inputs["T_surface"], "temperature")       # K
        Tinf = self._get_value(self.inputs["T_fluid"], "temperature")       # K

        q = h * A * (Ts - Tinf)  # W
        return HeatFlow(q)
