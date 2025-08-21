# processpi/pipelines/fittings.py

from typing import Optional, Dict, Union
from .base import PipelineBase
from ..units import *
from .standards import EQUIVALENT_LENGTHS, K_FACTORS


class Fitting(PipelineBase):
    """
    Represents a pipeline fitting or valve with either equivalent length or K-factor.

    Attributes:
        fitting_type (str): Type of fitting/valve (e.g., 'gate_valve_open', 'globe_valve').
        diameter (float): Inside diameter of the pipe (mm).
        quantity (int): Number of fittings of this type.
    """

    def __init__(
        self,
        fitting_type: str,
        diameter: Diameter,
        quantity: int = 1,
    ):
        self.fitting_type = fitting_type
        self.diameter = diameter
        self.quantity = quantity

        # Load equivalent length factor if available
        self.le_factor = EQUIVALENT_LENGTHS.get(fitting_type, None)

        # Load K-factor if available
        self.K = K_FACTORS.get(fitting_type, None)

    def equivalent_length(self) -> Optional[float]:
        """
        Calculate equivalent length of the fitting(s) in meters.

        Returns:
            float: Equivalent length (m) or None if not defined.
        """
        if self.le_factor is None:
            return None
        dj_m = self.diameter / 1000  # mm → m
        return self.le_factor * dj_m * self.quantity

    def total_K(self) -> Optional[float]:
        """
        Calculate total K-factor for the fitting(s).

        Returns:
            float: Total K-factor or None if not defined.
        """
        if self.K is None:
            return None
        return self.K * self.quantity

    def to_dict(self) -> Dict[str, Union[str, float, None]]:
        """
        Export fitting properties as dictionary for reporting.
        """
        return {
            "fitting_type": self.fitting_type,
            "diameter_mm": self.diameter,
            "quantity": self.quantity,
            "le_factor": self.le_factor,
            "equivalent_length_m": self.equivalent_length(),
            "K": self.K,
            "total_K": self.total_K(),
        }

    def calculate(self):
        """
        Perform the pipeline calculation (placeholder).
        """
        return self.to_dict()
