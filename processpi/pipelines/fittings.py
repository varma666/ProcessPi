from __future__ import annotations
from typing import Optional, Dict, Any
from ..units import Diameter, Length
from .standards import get_equivalent_length, get_k_factor


class Fitting:
    """
    Represents a pipe fitting for head loss and equivalent length calculations.
    """

    def __init__(
        self,
        fitting_type: str,
        diameter: Optional[Diameter] = None,
        quantity: int = 1,
    ):
        self.fitting_type = fitting_type
        self.diameter = diameter
        self.quantity = quantity

        # Validate quantity
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("`quantity` must be a positive integer.")

        # Validate diameter only if provided
        if diameter is not None and not isinstance(diameter, Diameter):
            raise TypeError("`diameter` must be a Diameter object from `processpi.units`.")

    def equivalent_length(self) -> Optional[Length]:
        """
        Returns the equivalent length (Le) for the fitting type.
        If Le depends on diameter and diameter is missing, raises a ValueError.
        """
        try:
            return get_equivalent_length(fitting_type=self.fitting_type)
        except ValueError as e:
            # Handle missing diameter case explicitly
            if "requires diameter" in str(e).lower():
                raise ValueError(
                    f"Diameter is required for calculating Le of '{self.fitting_type}'."
                ) from e
            return None

    def k_factor(self) -> Optional[float]:
        """
        Returns the K-factor for the fitting type.
        If K depends on diameter and diameter is missing, raises a ValueError.
        """
        try:
            return get_k_factor(self.fitting_type)
        except ValueError as e:
            if "requires diameter" in str(e).lower():
                raise ValueError(
                    f"Diameter is required for calculating K-factor of '{self.fitting_type}'."
                ) from e
            return None

    def calculate(self) -> Dict[str, Any]:
        """
        Returns a summary dictionary with fitting data and calculated values.
        """
        le = self.equivalent_length()
        k = self.k_factor()

        return {
            "fitting_type": self.fitting_type,
            "quantity": self.quantity,
            "diameter_in": self.diameter.to("in").value if self.diameter else None,
            "diameter_m": self.diameter.to("m").value if self.diameter else None,
            "equivalent_length_m": le.to("m").value if le else None,
            "k_factor": k,
        }

    def __repr__(self):
        return (
            f"Fitting(type={self.fitting_type}, "
            f"diameter={self.diameter}, quantity={self.quantity})"
        )
