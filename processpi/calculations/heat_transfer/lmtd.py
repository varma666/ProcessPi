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

        dT1 = self._get_value(self.inputs["dT1"], "temperature")
        dT2 = self._get_value(self.inputs["dT2"], "temperature")

        dTlm = dT1 if dT1 == dT2 else (dT1 - dT2) / math.log(dT1 / dT2)
        return dTlm
