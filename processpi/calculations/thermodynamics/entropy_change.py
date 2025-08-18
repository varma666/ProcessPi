from processpi.calculations.base import CalculationBase
import math

class EntropyChange(CalculationBase):
    """
    Calculate entropy change (ideal reversible process):
        ΔS = m * Cp * ln(T2/T1)
    """

    def validate_inputs(self):
        required = ["mass", "specific_heat", "temp_initial", "temp_final"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")
        if self.inputs["temp_initial"] <= 0 or self.inputs["temp_final"] <= 0:
            raise ValueError("Temperatures must be > 0 K for entropy calculation")

    def calculate(self):
        m = self._get_value(self.inputs["mass"], "mass")                     # kg
        Cp = self._get_value(self.inputs["specific_heat"], "specific_heat")  # J/kg·K
        T1 = self._get_value(self.inputs["temp_initial"], "temp_initial")    # K
        T2 = self._get_value(self.inputs["temp_final"], "temp_final")        # K

        ΔS = m * Cp * math.log(T2 / T1)
        return {"entropy_change_J_per_K": ΔS}
