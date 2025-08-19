from ..base import CalculationBase
from ...units import *

import math


class FluidVelocity(CalculationBase):
    """
    Calculate fluid velocity in a circular pipe.
    
    Formula:
        v = Q / A
          = 4Q / (πD²)
    
    Inputs:
        - volumetric_flow_rate (Q) [m³/s]
        - diameter (D) [m]
    
    Output:
        - velocity (v) [m/s]
    """

    def validate_inputs(self):
        required = ["volumetric_flow_rate", "diameter"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        Q = self._get_value(self.inputs["volumetric_flow_rate"], "volumetric_flow_rate")  # m³/s
        D = self._get_value(self.inputs["diameter"], "diameter") / 1000  # m

        A = math.pi * (D**2) / 4.0   # cross-sectional area [m²]
        v = Q / A                    # velocity [m/s]

        return Velocity(v, "m/s")
