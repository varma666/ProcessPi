from ..base import CalculationBase
from ...units import *

class PumpPower(CalculationBase):
    """
    A class to calculate the required pump power for a fluid system.

    This class computes both the hydraulic power (the power imparted to the fluid)
    and the shaft power (the power required at the pump's shaft, accounting for
    efficiency). The calculation is based on the fluid's flow rate, head, density,
    and the pump's mechanical efficiency.

    **Formulas:**
        * Hydraulic Power ($P_{hydraulic}$) = $ \rho \cdot g \cdot Q \cdot H $
        * Shaft Power ($P_{shaft}$) = $ P_{hydraulic} / \eta $

    Where:
        * $P_{hydraulic}$ = Hydraulic (water) power [W]
        * $P_{shaft}$ = Shaft power [W]
        * $ \rho $ = Fluid density [kg/m³]
        * $ g $ = Acceleration due to gravity (9.81 m/s²)
        * $ Q $ = Volumetric flow rate [m³/s]
        * $ H $ = Total dynamic head [m]
        * $ \eta $ = Pump efficiency [decimal]

    **Inputs:**
        * `flow_rate` (Q): The volumetric flow rate.
        * `head` (H): The total dynamic head.
        * `density` ($\rho$): The fluid's density.
        * `efficiency` ($\eta$): The pump's efficiency as a decimal (0 to 1).

    **Outputs:**
        * A dictionary containing two power values:
            * "hydraulic_power_W": The calculated hydraulic power in Watts.
            * "shaft_power_W": The calculated shaft power in Watts.
    """
        
    def validate_inputs(self):
        """
        Validates the required inputs for the calculation.

        This method checks for the presence of all necessary keys in the inputs
        dictionary and ensures that the efficiency is a valid value between 0 and 1.
        """
        # Ensure required inputs are present.
        required = ["flow_rate", "head", "density", "efficiency"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")
        
        # Ensure efficiency is a valid decimal between 0 and 1.
        efficiency = self.inputs["efficiency"]
        if not (0 < efficiency.value <= 1):
            raise ValueError("Efficiency must be between 0 and 1")

    def calculate(self):
        """
        Performs the pump power calculation.

        The method first calculates the hydraulic power and then the shaft power,
        accounting for the pump's efficiency.

        Returns:
            dict: A dictionary with the calculated hydraulic and shaft power.
        """
        # Define the gravitational constant.
        g = 9.81  # m/s²
        
        # Retrieve input values from the dictionary and convert them to base units.
        flow_rate = self._get_value(self.inputs["flow_rate"], "flow_rate")  # m³/s
        head = self._get_value(self.inputs["head"], "head")  # m
        density = self._get_value(self.inputs["density"], "density")  # kg/m³
        efficiency = self._get_value(self.inputs["efficiency"], "efficiency")  # decimal
        
        # Calculate the hydraulic power (the power transferred to the fluid).
        hydraulic_power = density * g * flow_rate * head
        
        # Calculate the shaft power (the power required at the pump's shaft).
        shaft_power = hydraulic_power / efficiency
        
        # Return a dictionary with the calculated power values.
        return {
            "hydraulic_power_W": hydraulic_power,
            "shaft_power_W": shaft_power
        }
