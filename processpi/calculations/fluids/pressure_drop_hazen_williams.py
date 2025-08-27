from ..base import CalculationBase
from ...units import *

class PressureDropHazenWilliams(CalculationBase):
    r"""
    A class to calculate the pressure drop in a pipe using the Hazen–Williams equation.

    The Hazen–Williams equation is an empirical formula for calculating head loss
    in a pipe due to friction. It is primarily used for water systems and is
    simpler than the Darcy-Weisbach equation as it does not require an iterative
    solution for the friction factor.

    **Formula (SI units):**
        $ h_f = 10.67 \cdot L \cdot Q^{1.852} / (C^{1.852} \cdot D^{4.87}) $

    **Where:**
        * $ h_f $ = head loss [m]
        * $ L $ = pipe length [m]
        * $ Q $ = volumetric flow rate [m³/s]
        * $ C $ = Hazen-Williams roughness coefficient [dimensionless]
        * $ D $ = pipe diameter [m]

    The pressure drop ($\Delta P$) is then calculated from the head loss ($h_f$)
    using the following relationship:
        $ \Delta P = \rho \cdot g \cdot h_f $

    **Inputs:**
        * `length`: The length of the pipe.
        * `flow_rate`: The volumetric flow rate of the fluid.
        * `coefficient`: The Hazen-Williams roughness coefficient.
        * `diameter`: The internal diameter of the pipe.
        * `density`: The density of the fluid.

    **Output:**
        * A `Pressure` object containing the calculated pressure drop in Pascals (Pa).
    """

    def validate_inputs(self):
        """
        Validates the required inputs for the calculation.

        This method checks for the presence of all necessary keys in the inputs
        dictionary and raises a ValueError if any are missing.
        """
        required = ["length", "flow_rate", "coefficient", "diameter", "density"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        """
        Performs the pressure drop calculation using the Hazen-Williams equation.

        The method first computes the head loss using the Hazen-Williams formula
        and then converts the head loss to pressure drop. The result is returned
        as a `Pressure` object.

        Returns:
            Pressure: The calculated pressure drop in Pascals.
        """
        # Retrieve input values from the dictionary and convert them to base SI units.
        L = self._get_value(self.inputs["length"], "length")        # m
        Q = self._get_value(self.inputs["flow_rate"], "flow_rate")      # m³/s
        C = self._get_value(self.inputs["coefficient"], "coefficient") # dimensionless
        D = self._get_value(self.inputs["diameter"], "diameter")        # m
        rho = self._get_value(self.inputs["density"], "density")        # kg/m³
        
        # Calculate the head loss (h_f) using the Hazen-Williams formula.
        # This formula is specific to SI units.
        h_f = 10.67 * L * (Q ** 1.852) / ((C ** 1.852) * (D ** 4.87))
        
        # Convert the calculated head loss (h_f) to pressure drop (delta_P)
        # using the relationship between pressure, density, and height.
        # The value 9.81 represents the acceleration due to gravity (g) in m/s².
        delta_P = rho * 9.81 * h_f
        
        # Return the final result as a Pressure object with the unit "Pa".
        return Pressure(delta_P, "Pa")
