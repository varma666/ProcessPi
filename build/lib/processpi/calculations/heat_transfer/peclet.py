from ..base import CalculationBase
from ...units import *

class PecletNumber(CalculationBase):
    """
    Peclet number (convection vs. conduction in fluid flow).

    **Formula:**
        Pe = Re * Pr
           = (ρ * v * L / μ) * (μ * Cp / k)
           = ρ * v * L * Cp / k
    """
    def validate_inputs(self):
        required = ["density", "velocity", "L", "Cp", "k"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        rho = self._get_value(self.inputs["density"], "density")
        v   = self._get_value(self.inputs["velocity"], "velocity")
        L   = self._get_value(self.inputs["L"], "length")
        Cp  = self._get_value(self.inputs["Cp"], "specific_heat")
        k   = self._get_value(self.inputs["k"], "thermal_conductivity")

        return Dimensionless((rho * v * L * Cp) / k)
