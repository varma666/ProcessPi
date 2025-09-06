from ..base import CalculationBase
from ...units import *

class CrossFlowSingleTube(CalculationBase):
    """
    Heat transfer to/from fluid flowing normal to a single tube.

    **Formula:**
        Q = h * A * (T_surface - T_fluid)

    **Inputs:**
        * `h`: Convective heat transfer coefficient [W/m²·K]
        * `diameter`: Tube outer diameter [m]
        * `length`: Tube length [m]
        * `T_surface`: Tube surface temperature [K]
        * `T_fluid`: Bulk fluid temperature [K]
    """

    def validate_inputs(self):
        required = ["h", "diameter", "length", "T_surface", "T_fluid"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        h = self._get_value(self.inputs["h"], "heat_transfer_coefficient")
        D = self._get_value(self.inputs["diameter"], "length")
        L = self._get_value(self.inputs["length"], "length")
        Ts = self._get_value(self.inputs["T_surface"], "temperature")
        Tinf = self._get_value(self.inputs["T_fluid"], "temperature")

        A = math.pi * D * L
        Q = h * A * (Ts - Tinf)
        return HeatFlow(Q)
