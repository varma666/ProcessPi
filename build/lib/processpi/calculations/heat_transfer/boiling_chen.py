from ..base import CalculationBase
from ...units import *

class ChenBoiling(CalculationBase):
    """
    Chen correlation for **flow boiling heat transfer**.

    **Formula (simplified):**
        h_total = S * h_pool + F * h_conv

    **Where:**
        * h_total = overall heat transfer coefficient [W/m²·K]
        * h_pool = pool boiling coefficient (from Rohsenow or others)
        * h_conv = forced convection coefficient (from Dittus-Boelter or similar)
        * S = suppression factor (empirical, function of Re, Boiling number, etc.)
        * F = enhancement factor (empirical, function of flow parameters)

    **Inputs:**
        * h_pool
        * h_conv
        * S
        * F

    **Output:**
        * HeatTransferCoefficient [W/m²·K]
    """

    def validate_inputs(self):
        required = ["h_pool", "h_conv", "S", "F"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        h_pool = self._get_value(self.inputs["h_pool"], "heat_transfer_coefficient")
        h_conv = self._get_value(self.inputs["h_conv"], "heat_transfer_coefficient")
        S      = self._get_value(self.inputs["S"], "dimensionless")
        F      = self._get_value(self.inputs["F"], "dimensionless")

        h_total = S * h_pool + F * h_conv
        return HeatTransferCoefficient(h_total)
