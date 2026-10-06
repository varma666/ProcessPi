from ..base import CalculationBase
from ...units import *

class GrashofNumber(CalculationBase):
    """
    Grashof number (buoyancy vs. viscous forces in natural convection).

    **Formula:**
        Gr = g * β * ΔT * L³ / ν²
    """
    def validate_inputs(self):
        required = ["g", "beta", "dT", "L", "nu"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        g   = self._get_value(self.inputs["g"], "acceleration")
        beta = self._get_value(self.inputs["beta"], "thermal_expansion_coefficient")
        dT  = self._get_value(self.inputs["dT"], "temperature")
        L   = self._get_value(self.inputs["L"], "length")
        nu  = self._get_value(self.inputs["nu"], "kinematic_viscosity")

        return Dimensionless((g * beta * dT * (L**3)) / (nu**2))
