from ..base import CalculationBase
from ...units import *

class PrandtlNumber(CalculationBase):
    """
    Prandtl number.

    **Formula:**
        Pr = μ * Cp / k
    """
    def validate_inputs(self):
        required = ["mu", "Cp", "k"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        mu = self._get_value(self.inputs["mu"], "dynamic_viscosity")
        Cp = self._get_value(self.inputs["Cp"], "specific_heat")
        k = self._get_value(self.inputs["k"], "thermal_conductivity")
        return Dimensionless(mu * Cp / k)
