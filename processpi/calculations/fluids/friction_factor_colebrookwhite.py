from ..base import CalculationBase
from ...units import *

import math


class ColebrookWhite(CalculationBase):
    """
    A class to calculate the Darcy friction factor using the Colebrook–White equation.

    The Colebrook-White equation is an empirical formula used to determine the Darcy
    friction factor (f) for fluid flow in pipes, particularly for turbulent flow.
    Because the equation is implicit, the friction factor must be solved for iteratively.

    **Formula (Implicit):**
        $ \frac{1}{\sqrt{f}} = -2.0 \cdot \log_{10} \left( \frac{\epsilon/D}{3.7} + \frac{2.51}{Re \cdot \sqrt{f}} \right) $

    **Inputs:**
        * `reynolds_number` (Re): A dimensionless quantity.
        * `diameter` (D): The internal diameter of the pipe.
        * `roughness` (ε): The absolute roughness of the pipe surface.

    **Output:**
        * A `Dimensionless` object containing the calculated friction factor (f).
    """

    def validate_inputs(self):
        """
        Validates the required inputs for the calculation.

        Ensures that 'reynolds_number', 'diameter', and 'roughness' are
        present in the inputs dictionary. Raises a ValueError if any key is missing.
        """
        required = ["reynolds_number", "diameter", "roughness"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
            """
            Calculates the Darcy friction factor.
            """
            # Retrieve and validate input values.
            Re = self._get_value(self.inputs["reynolds_number"], "reynolds_number")
            D = self._get_value(self.inputs["diameter"], "diameter")  # m
            eps = self._get_value(self.inputs["roughness"], "roughness")  # mm
    
            # Handle the special case of laminar flow
            if Re < 2000:
                f = 64.0 / Re
                return Dimensionless(f)
            
            # For turbulent flow, solve the Colebrook-White equation iteratively.
            f = 0.02
            tol = 1e-6
            max_iter = 100
    
            # CORRECTED LINE: Convert roughness from mm to m
            eps_m = eps / 1000.0
    
            for _ in range(max_iter):
                # Calculate both sides of the rearranged Colebrook-White equation.
                # Use the corrected 'eps_m' in the calculation
                rhs = -2.0 * math.log10((eps_m / (3.7 * D)) + (2.51 / (Re * math.sqrt(f))))
    
                # Calculate the new value of f based on the rhs.
                new_f = 1.0 / (rhs**2)
    
                if abs(new_f - f) < tol:
                    return Dimensionless(new_f)
                
                f = new_f
    
            return Dimensionless(f)

        # If the loop finishes without converging, return the last calculated value.
        return Dimensionless(f)
