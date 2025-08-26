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

        The method first checks if the flow is laminar (Re < 2000). If so, it
        uses the simple and direct formula f = 64/Re. For turbulent flow (Re >= 2000),
        it solves the implicit Colebrook-White equation iteratively.

        Returns:
            Dimensionless: The calculated Darcy friction factor.
        """
        # Retrieve and validate input values.
        Re = self._get_value(self.inputs["reynolds_number"], "reynolds_number")
        D = self._get_value(self.inputs["diameter"], "diameter")  # m
        eps = self._get_value(self.inputs["roughness"], "roughness")  # mm

        # Handle the special case of laminar flow, where the friction factor
        # is a simple, direct calculation and not an iterative one.
        if Re < 2000:
            f = 64.0 / Re
            return Dimensionless(f)

        # For turbulent flow, solve the Colebrook-White equation iteratively.
        # We start with a common initial guess for the friction factor.
        f = 0.02
        tol = 1e-6  # Tolerance for convergence
        max_iter = 100  # Maximum number of iterations to prevent an infinite loop

        for _ in range(max_iter):
            # Calculate both sides of the rearranged Colebrook-White equation.
            lhs = 1.0 / math.sqrt(f)
            rhs = -2.0 * math.log10((eps / (3.7 * D)) + (2.51 / (Re * math.sqrt(f))))

            # Calculate the new value of f based on the rhs.
            new_f = 1.0 / (rhs**2)

            # Check for convergence. If the change in f is less than the tolerance,
            # we have a stable solution and can return the result.
            if abs(new_f - f) < tol:
                return Dimensionless(new_f)
            
            # Update f for the next iteration.
            f = new_f

        # If the loop finishes without converging, return the last calculated value.
        return Dimensionless(f)
