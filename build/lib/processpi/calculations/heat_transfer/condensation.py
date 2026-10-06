import math
from ..base import CalculationBase
from ...units import *

class CondensingVapourFilm(CalculationBase):
    """
    Heat transfer from condensing vapours on a vertical plate (Nusselt’s theory).

    **Formula:**
        h = 0.943 * [ (ρ_l * (ρ_l - ρ_v) * g * h_fg * k_l^3) / (μ_l * L * ΔT) ]^(1/4)

    Then:
        Q = h * A * ΔT

    **Inputs:**
        * `rho_l`: Liquid density [kg/m³]
        * `rho_v`: Vapour density [kg/m³]
        * `g`: Gravity [m/s²]
        * `h_fg`: Latent heat [J/kg]
        * `k_l`: Liquid thermal conductivity [W/m·K]
        * `mu_l`: Liquid viscosity [Pa·s]
        * `L`: Plate length [m]
        * `A`: Area [m²]
        * `deltaT`: Temperature difference [K]
    """

    def validate_inputs(self):
        required = ["rho_l", "rho_v", "g", "h_fg", "k_l", "mu_l", "L", "A", "deltaT"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        rho_l = self._get_value(self.inputs["rho_l"], "density")
        rho_v = self._get_value(self.inputs["rho_v"], "density")
        g = self._get_value(self.inputs["g"], "acceleration")
        h_fg = self._get_value(self.inputs["h_fg"], "specific_energy")
        k_l = self._get_value(self.inputs["k_l"], "thermal_conductivity")
        mu_l = self._get_value(self.inputs["mu_l"], "dynamic_viscosity")
        L = self._get_value(self.inputs["L"], "length")
        A = self._get_value(self.inputs["A"], "area")
        dT = self._get_value(self.inputs["deltaT"], "temperature")

        h = 0.943 * ((rho_l * (rho_l - rho_v) * g * h_fg * k_l**3) / (mu_l * L * dT))**0.25
        Q = h * A * dT
        return HeatFlow(Q)
