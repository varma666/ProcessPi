from processpi.calculations.base import CalculationBase

class HeatOfVaporization(CalculationBase):
    """
    Calculate heat required for vaporization:
        Q = m * ΔHvap
    """

    def validate_inputs(self):
        required = ["mass", "heat_vaporization"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        m = self._get_value(self.inputs["mass"], "mass")                             # kg
        ΔHvap = self._get_value(self.inputs["heat_vaporization"], "heat_vaporization")  # J/kg

        Q = m * ΔHvap
        return {"heat_required_J": Q}
