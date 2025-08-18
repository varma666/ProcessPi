from ..base import CalculationBase
from ...units import *

class ConductionHeatLoss(CalculationBase):
    """
    Calculate steady-state conduction heat loss through a wall.
    Formula:
        Q = k * A * ΔT / L
    """

    def validate_inputs(self):
        required = ["thermal_conductivity", "area", "temp_difference", "thickness"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")
        if self.inputs["thickness"] <= 0:
            raise ValueError("Wall thickness must be greater than 0")

    def calculate(self):
        k = self._get_value(self.inputs["thermal_conductivity"], "thermal_conductivity")  # W/m·K
        A = self._get_value(self.inputs["area"], "area")                                  # m²
        ΔT = self._get_value(self.inputs["temp_difference"], "temp_difference")           # K
        L = self._get_value(self.inputs["thickness"], "thickness")                        # m

        Q = k * A * ΔT / L
        return HeatFlux(Q, "W")
