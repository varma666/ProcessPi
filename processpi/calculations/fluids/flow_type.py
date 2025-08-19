from ..base import CalculationBase
from ...units import *


class TypeOfFlow(CalculationBase):
    """
    Determine the type of flow based on Reynolds number.

    Criteria:
        - Laminar: Re < 2000
        - Transitional: 2000 ≤ Re ≤ 4000
        - Turbulent: Re > 4000

    Inputs:
        - reynolds_number (Re) [dimensionless]

    Output:
        - Flow type as a StringUnit
    """

    def validate_inputs(self):
        required = ["reynolds_number"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        Re = self._get_value(self.inputs["reynolds_number"], "reynolds_number")

        if Re < 2000:
            flow_type = "Laminar"
        elif 2000 <= Re <= 4000:
            flow_type = "Transitional"
        else:
            flow_type = "Turbulent"

        return StringUnit(flow_type, "flow_type")
