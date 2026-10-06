from ..base import CalculationBase
from ...units import *

class OverallHeatTransferCoefficient(CalculationBase):
    """
    Overall heat transfer coefficient for a composite wall.
    U = 1 / ΣR
    """
    def validate_inputs(self):
        if "resistances" not in self.inputs:
            raise ValueError("Missing required input: resistances")

    def calculate(self):
        Rs = [self._get_value(r, "thermal_resistance") for r in self.inputs["resistances"]]
        R_total = sum(Rs)
        return HeatTransferCoefficient(1 / R_total)
