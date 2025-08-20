# processpi/pipelines/fittings.py

from typing import Optional, Dict
from .base import PipelineBase
from ..units import *
from .standards import EQUIVALENT_LENGTHS


class Fitting(PipelineBase):
    """
    Represents a pipeline fitting or valve with equivalent length calculation.

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
        self.le_factor = EQUIVALENT_LENGTHS.get(fitting_type, None)

    def equivalent_length(self) -> Optional[float]:
        """
        Calculate equivalent length of the fitting(s) in meters.

        Returns:
            float: Equivalent length (m) or None if type not found.
        """
        if self.le_factor is None:
            return None
        # Le (m) = factor * Dj (m)
        dj_m = self.diameter / 1000  # mm → m
        return self.le_factor * dj_m * self.quantity

    def to_dict(self) -> Dict[str, Optional[float]]:
        """
        Export fitting properties as dictionary for reporting.
        """
        return {
            "fitting_type": self.fitting_type,
            "diameter_mm": self.diameter,
            "quantity": self.quantity,
            "le_factor": self.le_factor,
            "equivalent_length_m": self.equivalent_length(),
        }
    def calculate(self):
        """
        Perform the pipeline calculation.
        
        Must be implemented by subclasses.

        Returns:
            dict: Results of the calculation in key-value format.
        """
        pass