# processpi/calculations/fluids/optimum_pipe_diameter.py
from ..base import CalculationBase
from ...units import *
#

class OptimumPipeDiameter(CalculationBase):
    """
    Calculate the optimum pipe diameter using empirical formula and map to nearest standard:

        D_opt = 293 * (Q^0.53) * (ρ^-0.37)

    Where:
        - Q = Volumetric flow rate [m³/s]
        - ρ = Fluid density [kg/m³]
        - D_opt = Optimum diameter [mm]

    Inputs:
        - flow_rate (Q) [m³/s]
        - density (ρ) [kg/m³]

    Output:
        - Nearest standard diameter [Diameter object, mm]
    """

    def validate_inputs(self):
        required = ["flow_rate", "density"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        from ...pipelines.standards import get_nearest_diameter
        # Get inputs
        Q_volumetric = self._get_value(self.inputs["flow_rate"], "flow_rate")  # m³/s
        rho = self._get_value(self.inputs["density"], "density")  # kg/m³

        # Mass flow for formula
        Q_mass = Q_volumetric * rho  # kg/s

        # Empirical formula for optimum diameter
        D_opt = 293 * (Q_mass ** 0.53) * (rho ** -0.37)  # mm
        D_opt = Diameter(D_opt, "mm")

        # Map to nearest standard diameter
        nearest_std = get_nearest_diameter(D_opt)
        return nearest_std
