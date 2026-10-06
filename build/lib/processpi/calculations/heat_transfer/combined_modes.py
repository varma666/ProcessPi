from ..base import CalculationBase
from ...units import *

class ConductionConvectionCombined(CalculationBase):
    """
    Heat transfer with conduction resistance + convection resistance.

    **Formula:**
        Q = (Ts - T∞) / (R_cond + R_conv)

    Where:
        R_cond = dx / (k * A)
        R_conv = 1 / (h * A)

    **Inputs:**
        * `thickness`: Conduction thickness [m]
        * `k`: Thermal conductivity [W/m·K]
        * `h`: Convective coefficient [W/m²·K]
        * `area`: Heat transfer area [m²]
        * `T_surface`: Surface temperature [K]
        * `T_fluid`: Bulk fluid temperature [K]

    **Output:**
        * HeatFlow [W]
    """

    def validate_inputs(self):
        required = ["thickness", "k", "h", "area", "T_surface", "T_fluid"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        dx = self._get_value(self.inputs["thickness"], "length")
        k = self._get_value(self.inputs["k"], "thermal_conductivity")
        h = self._get_value(self.inputs["h"], "heat_transfer_coefficient")
        A = self._get_value(self.inputs["area"], "area")
        Ts = self._get_value(self.inputs["T_surface"], "temperature")
        Tinf = self._get_value(self.inputs["T_fluid"], "temperature")

        R_cond = dx / (k * A)
        R_conv = 1 / (h * A)

        Q = (Ts - Tinf) / (R_cond + R_conv)
        return HeatFlow(Q)
