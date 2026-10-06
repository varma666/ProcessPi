from ..base import CalculationBase
from ...units import *

class PressureDropFanning(CalculationBase):
    """
    A class to calculate the pressure drop in a pipe using the Fanning equation.

    The Fanning friction factor is a dimensionless number that relates the shear stress at the pipe wall to the kinetic energy of the fluid. The Fanning equation is widely used in chemical and process engineering for pressure drop calculations.

    **Formula:**
        $ \Delta P = 4 \cdot f_F \cdot \frac{L}{D} \cdot \frac{\rho \cdot v^2}{2} $

    Where:
        * $ \Delta P $ = Pressure drop [Pa]
        * $ f_F $ = Fanning friction factor [dimensionless]
        * $ L $ = Pipe length [m]
        * $ D $ = Pipe diameter [m]
        * $ \rho $ = Fluid density [kg/m³]
        * $ v $ = Fluid velocity [m/s]

    **Inputs:**
        * `friction_factor`: The Fanning friction factor of the pipe.
        * `length`: The length of the pipe.
        * `diameter`: The internal diameter of the pipe.
        * `density`: The density of the fluid.
        * `velocity`: The velocity of the fluid.

    **Output:**
        * A `Pressure` object containing the calculated pressure drop in Pascals (Pa).
    """

    def validate_inputs(self):
        """
        Validates the required inputs for the calculation.

        This method ensures all necessary keys are present in the inputs
        dictionary, raising a ValueError if any are missing.
        """
        required = ["friction_factor", "length", "diameter", "density", "velocity"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        """
        Performs the pressure drop calculation using the Fanning equation.

        Retrieves all required input values and applies the formula to compute
        the pressure drop. The result is returned as a `Pressure` object.

        Returns:
            Pressure: The calculated pressure drop in Pascals.
        """
        # Retrieve input values from the dictionary and ensure they are in the correct units.
        f = self._get_value(self.inputs["friction_factor"], "friction_factor")
        L = self._get_value(self.inputs["length"], "length")      # m
        D = self._get_value(self.inputs["diameter"], "diameter")    # m
        rho = self._get_value(self.inputs["density"], "density")    # kg/m³
        v = self._get_value(self.inputs["velocity"], "velocity")    # m/s

        # Apply the Fanning formula to calculate the pressure drop. Note the
        # factor of 4 difference from the Darcy-Weisbach equation.
        delta_P = 4 * f * (L / D) * (rho * v**2 / 2)
        
        # Return the result as a Pressure object with the unit "Pa".
        return Pressure(delta_P, "Pa")
