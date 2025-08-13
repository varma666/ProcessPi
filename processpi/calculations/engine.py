"""
engine.py
---------
This module will act as the central engine for performing calculations in ProcessPI.

Responsibilities:
1. Receive input parameters for a calculation.
2. Select the correct calculation class/function based on the requested operation.
3. Handle validation and error reporting.
4. Return results in a standardized format.
"""

from typing import Any, Dict, Type
from processpi.units import *  # Import all unit classes
from processpi.calculations import *  # Import all calculation classes

# Import calculation classes here
# Example: from processpi.calculations.heat_transfer import HeatTransferCalculator
# We'll add them as we implement each calculation
# For now, I'll just put placeholders for demonstration
# ----------------------------------------------------------------------

class CalculationEngine:
    """
    Central hub for all ProcessPI calculations.
    """

    def __init__(self):
        """
        Initializes the engine with a registry of available calculations.
        The registry maps calculation names (strings) to their handler classes.
        """
        self.registry: Dict[str, Type] = {}

    def register_calculation(self, name: str, calc_class: Type):
        """
        Register a new calculation class to the engine.

        Args:
            name (str): A unique string key for the calculation.
            calc_class (Type): The class that implements the calculation logic.

        Example:
            engine.register_calculation("heat_transfer", HeatTransferCalculator)
        """
        self.registry[name] = calc_class

    def calculate(self, name: str, **kwargs) -> Any:
        """
        Executes a calculation by name.

        Args:
            name (str): The registered name of the calculation.
            **kwargs: All input parameters required for the calculation.

        Returns:
            Any: The result of the calculation.
        
        Raises:
            ValueError: If the calculation name is not registered.
        """
        if name not in self.registry:
            raise ValueError(f"Calculation '{name}' not found in registry.")

        calc_class = self.registry[name]
        calc_instance = calc_class(**kwargs)  # Pass all inputs to the class constructor
        return calc_instance.calculate()  # All calculation classes must have a `.calculate()` method


