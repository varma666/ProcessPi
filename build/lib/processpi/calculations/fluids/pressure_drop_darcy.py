from ..base import CalculationBase
from ...units import *

class PressureDropDarcy(CalculationBase):
    """
    A class to calculate the pressure drop in a pipe using the Darcy–Weisbach equation.

    This formula is a widely used tool in fluid dynamics to calculate the loss of
    pressure due to friction along a given length of pipe. It is applicable for
    both laminar and turbulent flow regimes.

    **Formula:**
        $ \Delta P = f \cdot \frac{L}{D} \cdot \frac{\rho \cdot v^2}{2} $

    Where:
        * $ \Delta P $ = Pressure drop [Pa]
        * $ f $ = Darcy friction factor [dimensionless]
        * $ L $ = Pipe length [m]
        * $ D $ = Pipe diameter [m]
        * $ \rho $ = Fluid density [kg/m³]
        * $ v $ = Fluid velocity [m/s]

    **Inputs:**
        * `friction_factor`: The friction factor of the pipe.
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

        This method checks for the presence of all necessary keys in the inputs
        dictionary and raises a ValueError if any are missing.
        """
        required = ["friction_factor", "length", "diameter", "density", "velocity"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        """
        Performs the pressure drop calculation using the Darcy–Weisbach equation.

        Retrieves all required input values and applies the formula to compute
        the pressure drop. The result is returned as a `Pressure` object.

        Returns:
            Pressure: The calculated pressure drop in Pascals.
        """
        # Retrieve and validate input values.
        f = self._get_value(self.inputs["friction_factor"], "friction_factor")
        L = self._get_value(self.inputs["length"], "length")      # m
        D = self._get_value(self.inputs["diameter"], "diameter")    # m
        rho = self._get_value(self.inputs["density"], "density")    # kg/m³
        v = self._get_value(self.inputs["velocity"], "velocity")    # m/s
        #print(D)
        # Apply the Darcy-Weisbach formula to calculate the pressure drop.
        delta_P = f * (L / D) * (rho * v**2 / 2)
        
        # Return the result as a Pressure object with the unit "Pa".
        return Pressure(delta_P, "Pa")
