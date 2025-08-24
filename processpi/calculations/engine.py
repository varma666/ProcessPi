"""
engine.py
---------
This module acts as the central engine for performing calculations in ProcessPI.
"""

from typing import Any, Dict, Type
from processpi.units import *  # Import all unit classes

# Import calculation classes
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
    Central hub for all ProcessPI calculations.
    """

    def __init__(self):
        """
        Initializes the engine with a registry of available calculations.
        The registry maps calculation names (strings) to their handler classes.
        """
        self.registry: Dict[str, Type] = {}

        # Hardcoded registry initialization
        self._load_default_calculations()

    def _load_default_calculations(self):
        """
        Loads all available calculations into the registry.
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
        Dynamically register a new calculation class to the engine.
        """
        self.registry[name] = calc_class

    def calculate(self, name: str, **kwargs) -> Any:
        """
        Executes a calculation by name.
        """
        if name not in self.registry:
            raise ValueError(f"Calculation '{name}' not found in registry.")

        calc_class = self.registry[name]
        calc_instance = calc_class(**kwargs)
        return calc_instance.calculate()
