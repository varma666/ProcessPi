from ..base import CalculationBase
from ...units import *

import math


class FluidVelocity(CalculationBase):
    """
    A class to calculate the average fluid velocity in a circular pipe.

    This calculation is fundamental in fluid dynamics and is used to determine
    how quickly a fluid is moving through a pipe based on its volumetric flow
    rate and the pipe's cross-sectional area.

    **Formula:**
        $ v = \frac{Q}{A} = \frac{4 \cdot Q}{\pi \cdot D^2} $

    Where:
        * $ v $ = Fluid velocity [m/s]
        * $ Q $ = Volumetric flow rate [m³/s]
        * $ A $ = Cross-sectional area [m²]
        * $ D $ = Pipe diameter [m]

    **Inputs:**
        * `volumetric_flow_rate` (Q): The rate at which the fluid is flowing.
        * `diameter` (D): The internal diameter of the pipe.

    **Output:**
        * A `Velocity` object containing the calculated fluid velocity in meters per second (m/s).
    """

    def validate_inputs(self):
        """
        Validates the required inputs for the calculation.

        This method checks for the presence of all necessary keys in the inputs
        dictionary, raising a ValueError if any are missing.
        """
        required = ["volumetric_flow_rate", "diameter"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        """
        Performs the fluid velocity calculation.

        The method retrieves the volumetric flow rate and pipe diameter,
        calculates the cross-sectional area of the pipe, and then applies the
        formula to determine the fluid velocity.

        Returns:
            Velocity: The calculated fluid velocity in m/s.
        """
        # Retrieve input values from the dictionary and convert them to base units.
        Q = self._get_value(self.inputs["volumetric_flow_rate"], "volumetric_flow_rate")  # m³/s
        D = self._get_value(self.inputs["diameter"], "diameter")  # m

        # Calculate the cross-sectional area of the circular pipe.
        A = math.pi * (D**2) / 4.0  # m²
        
        # Calculate the fluid velocity using the flow rate and area.
        v = Q / A  # m/s

        # Return the result as a Velocity object with the unit "m/s".
        return Velocity(v, "m/s")
