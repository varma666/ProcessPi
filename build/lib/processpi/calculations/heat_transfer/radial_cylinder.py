import math
from ..base import CalculationBase
from ...units import *

class RadialHeatFlowCylinder(CalculationBase):
    """
    Radial heat conduction through a hollow cylinder.

    **Formula:**
        Q = (2 * π * k * L * (T1 - T2)) / ln(r2/r1)

    **Inputs:**
        * `k`: Thermal conductivity [W/m·K]
        * `length`: Cylinder length [m]
        * `r_inner`: Inner radius [m]
        * `r_outer`: Outer radius [m]
        * `T_inner`: Temperature at inner surface [K]
        * `T_outer`: Temperature at outer surface [K]

    **Output:**
        * HeatFlow [W]
    """

    def validate_inputs(self):
        required = ["k", "length", "r_inner", "r_outer", "T_inner", "T_outer"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        k = self._get_value(self.inputs["k"], "thermal_conductivity")
        L = self._get_value(self.inputs["length"], "length")
        r1 = self._get_value(self.inputs["r_inner"], "length")
        r2 = self._get_value(self.inputs["r_outer"], "length")
        T1 = self._get_value(self.inputs["T_inner"], "temperature")
        T2 = self._get_value(self.inputs["T_outer"], "temperature")

        Q = (2 * math.pi * k * L * (T1 - T2)) / math.log(r2 / r1)
        return HeatFlow(Q)
