from ..base import CalculationBase
from ...units import *

class DropwiseCondensation(CalculationBase):
    """
    Empirical correlations for **dropwise condensation**.

    Dropwise condensation has much higher heat transfer coefficients
    than filmwise (often 5–10× larger).

    **Simple empirical model:**
        h_dw = C * h_fw

    **Where:**
        * h_dw = dropwise condensation heat transfer coefficient [W/m²·K]
        * h_fw = filmwise condensation coefficient [W/m²·K] (from Nusselt theory)
        * C = enhancement factor (typically 5–10, depending on surface treatment)

    **Inputs:**
        * h_fw   – filmwise coefficient [W/m²·K]
        * C      – enhancement factor (default: 7)

    **Output:**
        * HeatTransferCoefficient [W/m²·K]
    """

    def validate_inputs(self):
        if "h_fw" not in self.inputs:
            raise ValueError("Missing required input: h_fw")

    def calculate(self):
        h_fw = self._get_value(self.inputs["h_fw"], "heat_transfer_coefficient")
        C    = self.inputs.get("C", 7.0)
        h_dw = C * h_fw
        return HeatTransferCoefficient(h_dw)
