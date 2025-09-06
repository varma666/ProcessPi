from ..base import CalculationBase
from ...units import *

class ThermalResistanceSeries(CalculationBase):
    """
    Equivalent thermal resistance for series layers.
    R_total = Σ Ri
    """
    def validate_inputs(self):
        if "resistances" not in self.inputs:
            raise ValueError("Missing required input: resistances")

    def calculate(self):
        Rs = [self._get_value(r, "thermal_resistance") for r in self.inputs["resistances"]]
        return ThermalResistance(sum(Rs))


class ThermalResistanceParallel(CalculationBase):
    """
    Equivalent thermal resistance for parallel layers.
    1/R_total = Σ (1/Ri)
    """
    def validate_inputs(self):
        if "resistances" not in self.inputs:
            raise ValueError("Missing required input: resistances")

    def calculate(self):
        Rs = [self._get_value(r, "thermal_resistance") for r in self.inputs["resistances"]]
        return ThermalResistance(1 / sum(1/r for r in Rs))
