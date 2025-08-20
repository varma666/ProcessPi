from ..base import CalculationBase
from ...units import *

import math


class ColebrookWhite(CalculationBase):
    """
    Calculate Darcy friction factor using the Colebrook–White equation.
    
    Formula (implicit):
        1/sqrt(f) = -2.0 * log10( (ε/D)/3.7 + 2.51/(Re*sqrt(f)) )
    
    Notes:
        - For laminar flow (Re < 2000), f = 64/Re.
        - Solved iteratively for turbulent flow.
    """

    def validate_inputs(self):
        required = ["reynolds_number", "diameter", "roughness"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        Re = self._get_value(self.inputs["reynolds_number"], "reynolds_number")
        D = self._get_value(self.inputs["diameter"], "diameter")  / 1000  # m
        eps = self._get_value(self.inputs["roughness"], "roughness")   # m

        # Laminar flow check
        if Re < 2000:
            f = 64.0 / Re
            return Dimensionless(f)

        # Initial guess
        f = 0.02
        tol = 1e-6
        max_iter = 100

        for _ in range(max_iter):
            lhs = 1.0 / math.sqrt(f)
            rhs = -2.0 * math.log10((eps / (3.7 * D)) + (2.51 / (Re * math.sqrt(f))))
            new_f = 1.0 / (rhs**2)

            if abs(new_f - f) < tol:
                return Dimensionless(new_f)
            f = new_f

        return Dimensionless(f)
