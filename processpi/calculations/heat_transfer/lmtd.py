import math
from ..base import CalculationBase
from ...units import *

class LMTD(CalculationBase):
    """
    Heat Exchanger using LMTD method.
    Q = U * A * ΔTlm
    """
    def validate_inputs(self):
        required = ["dT1", "dT2"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        eps = 1e-6

        dT1 = self._get_value(self.inputs["dT1"], "temperature")
        dT2 = self._get_value(self.inputs["dT2"], "temperature")

        if dT1 <= 0 or dT2 <= 0:
            raise ValueError("Invalid temperature approach in LMTD calculation.")

        dT1 = max(dT1, eps)
        dT2 = max(dT2, eps)

        if abs(dT1 - dT2) < eps:
            return dT1

        ratio = dT1 / dT2
        if ratio <= 0:
            raise ValueError("Invalid temperature approach in LMTD calculation.")

        return (dT1 - dT2) / math.log(ratio)
