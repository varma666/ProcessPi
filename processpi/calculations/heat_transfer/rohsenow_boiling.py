import math
from ..base import CalculationBase
from ...units import *

class RohsenowBoiling(CalculationBase):
    """
    Rohsenow correlation for **pool boiling heat transfer**.

    **Formula:**
        q'' = μ_l * h_fg * [ (g * (ρ_l - ρ_v) / σ)^(1/2) ] * [ Cp_l * (ΔT / (h_fg * Pr_l^n)) ]^3

    **Where:**
        * q'' = Heat flux [W/m²]
        * μ_l = Liquid viscosity [Pa·s]
        * h_fg = Latent heat of vaporization [J/kg]
        * g = Gravity [m/s²]
        * ρ_l, ρ_v = Liquid and vapor densities [kg/m³]
        * σ = Surface tension [N/m]
        * Cp_l = Specific heat of liquid [J/kg·K]
        * ΔT = (T_wall – T_sat) [K]
        * Pr_l = Prandtl number of liquid
        * n = empirical constant (usually 1.0 for water, 1.7 for other fluids)

    **Inputs:**
        * mu_l
        * h_fg
        * g
        * rho_l
        * rho_v
        * sigma
        * Cp_l
        * dT
        * Pr_l
        * n  (default: 1.0)

    **Output:**
        * HeatFlux [W/m²]
    """

    def validate_inputs(self):
        required = ["mu_l", "h_fg", "g", "rho_l", "rho_v", "sigma", "Cp_l", "dT", "Pr_l"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        mu_l  = self._get_value(self.inputs["mu_l"], "dynamic_viscosity")
        h_fg  = self._get_value(self.inputs["h_fg"], "specific_energy")
        g     = self._get_value(self.inputs["g"], "acceleration")
        rho_l = self._get_value(self.inputs["rho_l"], "density")
        rho_v = self._get_value(self.inputs["rho_v"], "density")
        sigma = self._get_value(self.inputs["sigma"], "surface_tension")
        Cp_l  = self._get_value(self.inputs["Cp_l"], "specific_heat")
        dT    = self._get_value(self.inputs["dT"], "temperature")
        Pr_l  = self._get_value(self.inputs["Pr_l"], "dimensionless")
        n     = self.inputs.get("n", 1.0)

        term1 = mu_l * h_fg * math.sqrt(g * (rho_l - rho_v) / sigma)
        term2 = (Cp_l * dT / (h_fg * (Pr_l ** n))) ** 3
        q_flux = term1 * term2

        return HeatFlux(q_flux)
