from ..base import CalculationBase
from ...units import *


class OptimumPipeDiameter(CalculationBase):
    """
    Calculate the optimum pipe diameter using empirical formula:

        D_opt = 293 * (Q^0.53) * (ρ^-0.37)

    Where:
        - Q = Volumetric flow rate [m³/s]
        - ρ = Fluid density [kg/m³]
        - D_opt = Optimum diameter [mm]

    Inputs:
        - flow_rate (Q) [m³/s]
        - density (ρ) [kg/m³]

    Output:
        - Optimum diameter [mm]
    """

    def validate_inputs(self):
        required = ["flow_rate", "density"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        Q_volumetric = self._get_value(self.inputs["flow_rate"], "flow_rate")  # m³/s
        rho = self._get_value(self.inputs["density"], "density")  # kg/m³
        Q = Q_volumetric * rho  # kg/s

        # Formula
        D_opt = 293 * (Q ** 0.53) * (rho ** -0.37)  # mm
        #print(f"Calculated Optimum Diameter: {D_opt} mm")

        return Diameter(D_opt , "mm")  
