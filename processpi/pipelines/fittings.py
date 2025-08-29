# processpi/pipelines/fittings.py

from typing import Optional, Dict, Union
import difflib
from .base import PipelineBase
from ..units import *
from .standards import EQUIVALENT_LENGTHS, K_FACTORS


def _validate_fitting_type(fitting_type: str) -> None:
    """
    Validates that the given fitting_type exists in the standards database.

    Raises:
        ValueError: If the fitting_type is not found, with a suggested closest match.
    """
    valid_types = sorted(set(EQUIVALENT_LENGTHS) | set(K_FACTORS))
    if fitting_type not in valid_types:
        suggestion = difflib.get_close_matches(fitting_type, valid_types, n=1)
        hint = f" Did you mean '{suggestion[0]}'?" if suggestion else ""
        raise ValueError(
            f"Invalid fitting type '{fitting_type}'.{hint}\n"
            f"Valid fittings are: {', '.join(valid_types)}"
        )


class Fitting(PipelineBase):
    """
    Represents a pipeline fitting or valve used to calculate minor losses in a
    fluid network.

    Minor losses are head losses caused by the disturbance of flow due to
    changes in pipe geometry, such as bends, junctions, and valves. They are
    typically calculated using either the equivalent length method or the
    K-factor (resistance coefficient) method. This class supports both.
    """

    def __init__(
        self,
        fitting_type: str,
        diameter: Optional[Diameter] = None,
        quantity: int = 1,
    ):
        """
        Initializes a Fitting instance.

        Args:
            fitting_type (str): The name of the fitting type. Must match a key
                                in the standards databases (EQUIVALENT_LENGTHS or K_FACTORS).
            diameter (Diameter): The inside diameter of the pipe as a `Diameter` object.
            quantity (int, optional): The number of this type of fitting. Defaults to 1.
        """
        if not isinstance(diameter, Diameter):
            raise TypeError("`diameter` must be a Diameter object from `processpi.units`.")

        # Validate fitting type
        _validate_fitting_type(fitting_type)

        self.fitting_type: str = fitting_type
        self.diameter: Diameter = diameter
        self.quantity: int = quantity

        # Load standard factors based on the fitting_type
        self.le_factor: Optional[float] = EQUIVALENT_LENGTHS.get(fitting_type, None)
        self.K: Optional[float] = K_FACTORS.get(fitting_type, None)

    def equivalent_length(self) -> Optional[Variable]:
        """
        Calculates the total equivalent length (Le) of the fitting(s) in meters.
        """
        if self.le_factor is None:
            return None

        diameter_m = self.diameter.to("m").value
        total_le_m = self.le_factor * diameter_m * self.quantity

        return Variable(total_le_m, "m")

    def total_K(self) -> Optional[float]:
        """
        Calculates the total resistance coefficient (K-factor) for the fitting(s).
        """
        if self.K is None:
            return None
        return self.K * self.quantity

    def to_dict(self) -> Dict[str, Union[str, float, int, None]]:
        """
        Exports the fitting's properties and calculated values as a dictionary.
        """
        equivalent_length = self.equivalent_length()
        if equivalent_length is not None:
            equivalent_length = equivalent_length.value

        return {
            "fitting_type": self.fitting_type,
            "diameter_mm": self.diameter.value,
            "quantity": self.quantity,
            "le_factor": self.le_factor,
            "equivalent_length_m": equivalent_length,
            "K": self.K,
            "total_K": self.total_K(),
        }

    def calculate(self):
        """Returns the fitting's data dictionary for reporting/calculations."""
        return self.to_dict()

    def __repr__(self) -> str:
        """Developer-friendly string representation of the object."""
        return (f"Fitting(type='{self.fitting_type}', diameter={self.diameter}, "
                f"quantity={self.quantity})")
