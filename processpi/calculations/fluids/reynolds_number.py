from ..base import CalculationBase
from ...units import *

class ReynoldsNumber(CalculationBase):
    """
    A class to calculate the Reynolds number for fluid flow in a pipe.

    The Reynolds number (Re) is a dimensionless quantity that helps predict
    the flow patterns in a fluid. It represents the ratio of inertial forces to
    viscous forces. A low Reynolds number indicates laminar flow, while a high
    Reynolds number indicates turbulent flow.

    **Formulas:**
        * Using dynamic viscosity ($\mu$): $ Re = \frac{\rho \cdot v \cdot D}{\mu} $
        * Using kinematic viscosity ($\nu$): $ Re = \frac{v \cdot D}{\nu} $

    **Where:**
        * $ \rho $ = Fluid density [kg/m³]
        * $ v $ = Fluid velocity [m/s]
        * $ D $ = Pipe diameter [m]
        * $ \mu $ = Dynamic viscosity [Pa·s]
        * $ \nu $ = Kinematic viscosity [m²/s]

    **Inputs:**
        * `density`: The fluid's density.
        * `velocity`: The fluid's velocity.
        * `diameter`: The internal diameter of the pipe.
        * `viscosity`: The fluid's viscosity (can be dynamic or kinematic).

    **Output:**
        * A `Dimensionless` object containing the calculated Reynolds number.
    """

    def validate_inputs(self):
        """
        Validates the required inputs for the calculation.

        This method checks for the presence of all necessary keys in the inputs
        dictionary, raising a ValueError if any are missing.
        """
        required = ["density", "velocity", "diameter", "viscosity"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        """
        Performs the Reynolds number calculation based on the type of viscosity provided.

        The method first retrieves all required input values. It then determines
        whether the input viscosity is dynamic or kinematic and applies the
        appropriate formula to calculate the Reynolds number.

        Returns:
            Dimensionless: The calculated Reynolds number.
        """
        # Retrieve input values from the dictionary and convert them to base units.
        rho = self._get_value(self.inputs["density"], "density")       # kg/m³
        v = self._get_value(self.inputs["velocity"], "velocity")       # m/s
        D = self._get_value(self.inputs["diameter"], "diameter")       # m
        viscosity = self.inputs["viscosity"]
        #print(D,v,rho,viscosity)
        # Check the type of viscosity provided (dynamic or kinematic) and apply
        # the corresponding formula to calculate the Reynolds number.
        if viscosity.viscosity_type == "dynamic":
            mu = self._get_value(viscosity.to("Pa·s"), "viscosity")  # Pa·s
            Re = (rho * v * D) / mu
        else:
            nu = self._get_value(viscosity.to("m2/s"), "viscosity")  # m²/s
            Re = (v * D) / nu
            
        # Return the result as a Dimensionless object.
        return Dimensionless(Re)
