from .base import CalculationBase

class PumpPower(CalculationBase):
    """
    Calculate pump power from flow rate, head, density, and efficiency.
    """
        
    def validate_inputs(self):
        # Ensure required inputs are present and valid
        required = ["flow_rate", "head", "density", "efficiency"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")
        if not (0 < self.inputs["efficiency"] <= 1):
            raise ValueError("Efficiency must be between 0 and 1")

    def calculate(self):
        g = 9.81  # m/s²
        flow_rate = self._get_value(self.inputs["flow_rate"], "flow_rate")  # m³/s
        head = self._get_value(self.inputs["head"], "head")  # m
        density = self._get_value(self.inputs["density"], "density")  # kg/m³
        efficiency = self._get_value(self.inputs["efficiency"], "efficiency")  # decimal

        # Hydraulic Power (Watts)
        hydraulic_power = density * g * flow_rate * head

        # Shaft Power (Watts)
        shaft_power = hydraulic_power / efficiency

        return {
            "hydraulic_power_W": hydraulic_power,
            "shaft_power_W": shaft_power
        }
