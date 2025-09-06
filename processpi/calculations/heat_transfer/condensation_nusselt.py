import math
from ..base import CalculationBase
from ...units import *

class NusseltCondensation(CalculationBase):
    """
    Filmwise condensation heat transfer coefficient
    based on **Nusselt’s theory** (laminar film condensation on vertical surface).

    **Formula (vertical plate/tube):**
        h = 0.943 * [ (k_l^3 * rho_l^2 * g * h_fg) / (mu_l * L * ΔT) ]^(1/4)

    **Where:**
        * h = average heat transfer coefficient [W/m²·K]
        * k_l = liquid thermal conductivity [W/m·K]
        * rho_l = liquid density [kg/m³]
        * g = gravity [m/s²]
        * h_fg = latent heat of vaporization [J/kg]
        * mu_l = liquid viscosity [Pa·s]
        * L = characteristic length (plate height or tube length) [m]
        * ΔT = (T_wall – T_sat) [K]

    **Inputs:**
        * k_l
        * rho_l
        * g
        * h_fg
        * mu_l
        * L
        * dT

    **Output:**
        * HeatTransferCoefficient [W/m²·K]
    """

    def validate_inputs(self):
        required = ["k_l", "rho_l", "g", "h_fg", "mu_l", "L", "dT"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        k_l   = self._get_value(self.inputs["k_l"], "thermal_conductivity")
        rho_l = self._get_value(self.inputs["rho_l"], "density")
        g     = self._get_value(self.inputs["g"], "acceleration")
        h_fg  = self._get_value(self.inputs["h_fg"], "specific_energy")
        mu_l  = self._get_value(self.inputs["mu_l"], "dynamic_viscosity")
        L     = self._get_value(self.inputs["L"], "length")
        dT    = self._get_value(self.inputs["dT"], "temperature")

        h = 0.943 * ((k_l**3 * rho_l**2 * g * h_fg) / (mu_l * L * dT)) ** 0.25
        return HeatTransferCoefficient(h)
