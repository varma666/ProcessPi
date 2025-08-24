from ..base import CalculationBase
from ...units import *

class ReynoldsNumber(CalculationBase):
    """
    Calculate Reynolds number for pipe flow.
    Formula:
        Re = (ρ * v * D) / μ
    """

    def validate_inputs(self):
        required = ["density", "velocity", "diameter", "viscosity"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        rho = self._get_value(self.inputs["density"], "density")    # kg/m³
        v = self._get_value(self.inputs["velocity"], "velocity")    # m/s
        D = self._get_value(self.inputs["diameter"], "diameter")    # m
        viscosity = self.inputs["viscosity"]

        if viscosity.viscosity_type == "dynamic":
            mu = self._get_value(viscosity.to("Pa·s"), "viscosity")  # Pa·s
            Re = rho * v * D / mu
        else:
            nu = self._get_value(viscosity.to("m2/s"), "viscosity")  # m²/s
            Re = v * D / nu

        return Dimensionless(Re)

