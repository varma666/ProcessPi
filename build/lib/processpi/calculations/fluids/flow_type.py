from ..base import CalculationBase
from ...units import *


class TypeOfFlow(CalculationBase):
    """
    A class to determine the type of fluid flow based on the Reynolds number.

    This class serves as a calculation engine for classifying flow regimes as
    Laminar, Transitional, or Turbulent according to standard engineering criteria.
    It inherits from `CalculationBase` to ensure a standardized input/output
    structure.

    **Flow Regime Criteria:**
        * Laminar Flow: Occurs when the fluid moves in smooth, parallel layers, with little to no mixing. This regime is defined by a Reynolds number (Re) less than 2000.
        * Transitional Flow: An unstable regime where the flow can fluctuate between laminar and turbulent characteristics. It is defined by a Reynolds number between 2000 and 4000 (inclusive).
        * Turbulent Flow: Characterized by chaotic, unpredictable fluid motion with significant mixing. This regime is defined by a Reynolds number greater than 4000.

    **Inputs:**
        * `reynolds_number` (Re): A dimensionless quantity representing the ratio of inertial forces to viscous forces.

    **Output:**
        * A `StringUnit` containing the determined flow type ("Laminar", "Transitional", or "Turbulent").
    """

    def validate_inputs(self):
        """
        Validates the required inputs for the calculation.

        Ensures that the 'reynolds_number' key is present in the inputs dictionary.
        Raises a ValueError if the key is missing.
        """
        required = ["reynolds_number"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        """
        Performs the calculation to determine the flow type.

        Retrieves the Reynolds number from the inputs and applies the flow regime
        criteria to classify the flow.

        Returns:
            StringUnit: An object containing the flow type as a string.
        """
        # Retrieve the Reynolds number value from the inputs.
        Re = self._get_value(self.inputs["reynolds_number"], "reynolds_number")

        # Determine the flow type based on the Reynolds number value.
        if Re < 2000:
            flow_type = "Laminar"
        elif 2000 <= Re <= 4000:
            flow_type = "Transitional"
        else:
            flow_type = "Turbulent"

        # Return the result as a StringUnit object.
        return StringUnit(flow_type, "flow_type")
