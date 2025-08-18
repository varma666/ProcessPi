from ..base import CalculationBase
from ...units import *

class PressureDropFanning(CalculationBase):
    """
    Calculate pressure drop using Fanning equation.
    Formula:
        ΔP = 4 * f * (L/D) * (ρ * v² / 2)
    """

    def validate_inputs(self):
        required = ["friction_factor", "length", "diameter", "density", "velocity"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        f = self._get_value(self.inputs["friction_factor"], "friction_factor")
        L = self._get_value(self.inputs["length"], "length")        # m
        D = self._get_value(self.inputs["diameter"], "diameter")    # m
        rho = self._get_value(self.inputs["density"], "density")    # kg/m³
        v = self._get_value(self.inputs["velocity"], "velocity")    # m/s

        delta_P = 4 * f * (L / D) * (rho * v**2 / 2)
        return Pressure(delta_P, "Pa")  # Return result as Pressure object
