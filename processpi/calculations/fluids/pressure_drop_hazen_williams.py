from ..base import CalculationBase
from ...units import *

class PressureDropHazenWilliams(CalculationBase):
    """
    Calculate pressure drop using the Hazen-Williams equation.
    
    Formula (SI units):
        h_f = 10.67 * L * Q^1.852 / (C^1.852 * D^4.87)
    
    where:
        h_f = head loss (m)
        L   = pipe length (m)
        Q   = volumetric flow rate (m³/s)
        C   = Hazen-Williams roughness coefficient (dimensionless)
        D   = pipe diameter (m)
    
    Pressure drop:
        ΔP = ρ * g * h_f
    """

    def validate_inputs(self):
        required = ["length", "flow_rate", "coefficient", "diameter", "density"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        # Extract and convert inputs
        L = self._get_value(self.inputs["length"], "length")           # m
        Q = self._get_value(self.inputs["flow_rate"], "flow_rate")     # m³/s
        C = self._get_value(self.inputs["coefficient"], "coefficient") # dimensionless
        D = self._get_value(self.inputs["diameter"], "diameter")       # m
        rho = self._get_value(self.inputs["density"], "density")       # kg/m³

        # Hazen-Williams head loss (m)
        h_f = 10.67 * L * (Q ** 1.852) / ((C ** 1.852) * (D ** 4.87))

        # Convert to pressure drop (Pa)
        delta_P = rho * 9.81 * h_f

        return Pressure(delta_P, "Pa")
