from ..base import CalculationBase
from ...units import *

import math


class OptimumPipeDiameter(CalculationBase):
    """
    A class to calculate the optimum pipe diameter using an empirical formula.

    This class provides a method for calculating the most efficient pipe diameter
    for a given set of fluid properties and flow rate, based on an empirical
    correlation. The calculated optimum diameter is then mapped to the nearest
    available standard pipe size.

    **Empirical Formula:**
        $D_{opt} = 293 \cdot Q_{mass}^{0.53} \cdot \rho^{-0.37}$

    Where:
        * $D_{opt}$ = Optimum diameter [mm]
        * $Q_{mass}$ = Mass flow rate [kg/s]
        * $\rho$ = Fluid density [kg/m³]

    **Inputs:**
        * `flow_rate` (Q): The volumetric flow rate of the fluid.
        * `density` ($\rho$): The density of the fluid.

    **Output:**
        * The nearest standard pipe diameter as a `Diameter` object in millimeters.
    """

    def validate_inputs(self):
        """
        Validates the required inputs for the calculation.

        This method ensures that the 'flow_rate' and 'density' keys are present
        in the inputs dictionary, raising a ValueError if any required input is missing.
        """
        required = ["flow_rate", "density"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        """
        Performs the calculation to find the optimum and nearest standard pipe diameter.

        The method first calculates the mass flow rate from the volumetric flow
        rate and density. It then applies the empirical formula to find the
        optimum diameter. Finally, it uses an external utility function to find
        the closest standard pipe size and returns it.

        Returns:
            Diameter: The nearest standard pipe diameter.
        """
        from ...pipelines.standards import get_nearest_diameter
        
        # Retrieve input values from the dictionary and convert them to base units (m³/s and kg/m³).
        Q_volumetric = self._get_value(self.inputs["flow_rate"], "flow_rate")  # m³/s
        rho = self._get_value(self.inputs["density"], "density")  # kg/m³

        # Calculate the mass flow rate (Q_mass) as it is required by the empirical formula.
        Q_mass = Q_volumetric * rho  # kg/s

        # Apply the empirical formula for the optimum pipe diameter.
        D_opt = 293 * (Q_mass ** 0.53) * (rho ** -0.37)  # The formula returns the diameter in mm
        D_opt = Diameter(D_opt, "mm")

        # Use the utility function to map the calculated optimum diameter to the nearest standard size.
        nearest_std = get_nearest_diameter(D_opt)
        
        # Return the final result.
        return nearest_std
