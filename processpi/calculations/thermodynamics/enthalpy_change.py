from ..base import CalculationBase
from ...units import *

class EnthalpyChange(CalculationBase):
    """
    Calculate enthalpy change using:
        ΔH = m * Cp * ΔT
    """

    def validate_inputs(self):
        required = ["mass", "specific_heat", "temp_initial", "temp_final"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        m = self._get_value(self.inputs["mass"], "mass")                     # kg
        Cp = self._get_value(self.inputs["specific_heat"], "specific_heat")  # J/kg·K
        T1 = self._get_value(self.inputs["temp_initial"], "temp_initial")    # °C or K
        T2 = self._get_value(self.inputs["temp_final"], "temp_final")        # °C or K

        ΔH = m * Cp * (T2 - T1)
        return EnthalpyChange(ΔH, "J")
