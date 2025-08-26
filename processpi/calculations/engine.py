"""
This module acts as the central engine for performing calculations in the ProcessPI library.

The `CalculationEngine` class serves as a central hub, providing a registry for
all available calculation classes. This design allows users to execute
calculations by name without needing to directly import or instantiate each class.
"""

from typing import Any, Dict, Type
from processpi.units import * # Import all unit classes

# Import all calculation classes for the registry. This makes them available to the engine.
from processpi.calculations.fluids.velocity import FluidVelocity
from processpi.calculations.fluids.reynolds_number import ReynoldsNumber
from processpi.calculations.fluids.friction_factor_colebrookwhite import ColebrookWhite
from processpi.calculations.fluids.pressure_drop_darcy import PressureDropDarcy
from processpi.calculations.fluids.pressure_drop_fanning import PressureDropFanning
from processpi.calculations.fluids.pressure_drop_hazen_williams import PressureDropHazenWilliams
# Add more imports here as you implement new calculations
# from processpi.calculations.fluids.pressure_drop import PressureDrop
# from processpi.calculations.heat_transfer import HeatTransfer

class CalculationEngine:
    """
    The central hub for all ProcessPI calculations.

    The engine maintains a registry of calculation classes and provides a
    single, consistent method to execute any registered calculation by its name.
    This decouples the calling code from the specific implementation details
    of each calculation.
    """

    def __init__(self):
        """
        Initializes the engine with a registry of available calculations.

        The registry maps calculation names (strings) to their handler classes.
        This provides a dynamic lookup table for the `calculate` method.
        """
        self.registry: Dict[str, Type] = {}

        # Load the default, hardcoded set of calculations into the registry.
        self._load_default_calculations()

    def _load_default_calculations(self):
        """
        Loads all available calculations into the registry.

        This private method populates the registry with calculation classes
        and their associated string names and aliases, such as 're' for
        'reynolds_number'.
        """
        self.registry = {
            "fluid_velocity": FluidVelocity,
            "velocity": FluidVelocity,
            "v": FluidVelocity,
            "volumetric_flow_rate": FluidVelocity,
            "nre": ReynoldsNumber,
            "reynolds_number": ReynoldsNumber,
            "re": ReynoldsNumber,
            "reynoldsnumber": ReynoldsNumber,
            "colebrook_white": ColebrookWhite,
            "friction_factor_colebrookwhite": ColebrookWhite,
            "friction_factor": ColebrookWhite,
            "ff": ColebrookWhite,
            "pressure_drop_darcy": PressureDropDarcy,
            "pd": PressureDropDarcy,
            "pressure_drop": PressureDropDarcy,
            "pressure_drop_fanning": PressureDropFanning,
            "pressure_drop_hazen_williams": PressureDropHazenWilliams,

            # Add more mappings as new calculations are added
            # "pressure_drop": PressureDrop,
            # "heat_transfer": HeatTransfer,
        }

    def register_calculation(self, name: str, calc_class: Type):
        """
        Dynamically registers a new calculation class with the engine.

        This method allows for extending the engine's capabilities at runtime
        without modifying the source code.

        Args:
            name (str): The string name to be used for the calculation.
            calc_class (Type): The calculation class to register.
        """
        self.registry[name] = calc_class

    def calculate(self, name: str, **kwargs) -> Any:
        """
        Executes a calculation by its registered name.

        The method looks up the calculation class in the registry,
        instantiates it with the provided keyword arguments, and then runs
        its `calculate` method.

        Args:
            name (str): The name of the calculation to execute.
            **kwargs: Arbitrary keyword arguments to be passed as inputs to
                      the calculation class.

        Returns:
            Any: The result of the calculation, as returned by the
                 `calculate` method of the specific class.

        Raises:
            ValueError: If the specified calculation name is not found in the registry.
        """
        if name not in self.registry:
            raise ValueError(f"Calculation '{name}' not found in registry.")

        # Get the class from the registry and instantiate it with inputs.
        calc_class = self.registry[name]
        calc_instance = calc_class(**kwargs)
        
        # Run the calculation and return the result.
        return calc_instance.calculate()
