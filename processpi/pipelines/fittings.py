# processpi/pipelines/fittings.py

from typing import Optional, Dict, Union
from .base import PipelineBase
from ..units import Diameter, UnitfulValue
from .standards import EQUIVALENT_LENGTHS, K_FACTORS


class Fitting(PipelineBase):
    """
    Represents a pipeline fitting or valve used to calculate minor losses in a
    fluid network.

    Minor losses are head losses caused by the disturbance of flow due to
    changes in pipe geometry, such as bends, junctions, and valves. They are
    typically calculated using either the equivalent length method or the
    K-factor (resistance coefficient) method. This class supports both.

    Attributes:
        fitting_type (str): A string identifying the type of fitting, which
                            is used to look up standard values from a database.
                            (e.g., 'gate_valve_open', '90_deg_standard_elbow').
        diameter (Diameter): The nominal or inside diameter of the pipe to
                             which the fitting is attached.
        quantity (int): The number of identical fittings in a series.
        le_factor (Optional[float]): The equivalent length factor (L/D) for the
                                     fitting type, loaded from the standards database.
                                     This value is dimensionless.
        K (Optional[float]): The resistance coefficient (K-factor) for the
                             fitting type, loaded from the standards database.
                             This value is dimensionless.
    """

    def __init__(
        self,
        fitting_type: str,
        diameter: Diameter,
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
        
        self.fitting_type: str = fitting_type
        self.diameter: Diameter = diameter
        self.quantity: int = quantity

        # Load standard factors based on the fitting_type. These are
        # typically sourced from engineering handbooks (e.g., Crane 410).
        self.le_factor: Optional[float] = EQUIVALENT_LENGTHS.get(fitting_type, None)
        self.K: Optional[float] = K_FACTORS.get(fitting_type, None)

        if self.le_factor is None and self.K is None:
            print(f"Warning: No standard data found for fitting_type '{fitting_type}'. "
                  "Calculations for this fitting may not be possible.")
            
    def equivalent_length(self) -> Optional[UnitfulValue]:
        """
        Calculates the total equivalent length (Le) of the fitting(s) in meters.

        The formula used is:
        $L_e = (L/D) \times D_{pipe} \times N$
        where $L/D$ is the equivalent length factor, $D_{pipe}$ is the pipe
        diameter, and $N$ is the quantity of fittings.

        Returns:
            Optional[UnitfulValue]: The total equivalent length as a `UnitfulValue`
                                    in meters, or `None` if the L/D factor is not available.
        """
        if self.le_factor is None:
            return None
        
        # Ensure diameter is in meters for the calculation.
        diameter_m = self.diameter.to("m").value
        total_le_m = self.le_factor * diameter_m * self.quantity
        
        return UnitfulValue(total_le_m, "m")

    def total_K(self) -> Optional[float]:
        """
        Calculates the total resistance coefficient (K-factor) for the fitting(s).

        The formula used is:
        $K_{total} = K \times N$
        where $K$ is the resistance coefficient for a single fitting and
        $N$ is the quantity of fittings.

        Returns:
            Optional[float]: The total K-factor, or `None` if the K-factor is not available.
        """
        if self.K is None:
            return None
            
        return self.K * self.quantity

    def to_dict(self) -> Dict[str, Union[str, float, int, None]]:
        """
        Exports the fitting's properties and calculated values as a dictionary.
        This is useful for logging, reporting, or data serialization.
        
        Returns:
            Dict[str, Union[str, float, int, None]]: A dictionary containing
                                                      the fitting's attributes and
                                                      calculation results.
        """
        # Ensure UnitfulValue attributes are converted to their base value for the dict.
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
        """
        A placeholder method for consistency with other `PipelineBase` objects.
        In this context, it simply returns the serialized dictionary of results.
        """
        return self.to_dict()

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the object.
        """
        return (f"Fitting(type='{self.fitting_type}', diameter={self.diameter}, "
                f"quantity={self.quantity})")
