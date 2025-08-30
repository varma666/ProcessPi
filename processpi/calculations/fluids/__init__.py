"""
Initializes the Process PI calculation engine module for fluid mechanics.

This module dynamically discovers and imports all calculation classes 
from Python files in this folder, so you don’t need to manually update 
this __init__.py whenever a new calculation is added.

Available calculations include:
    * PressureDropDarcy
    * PressureDropFanning
    * PumpPower
    * ReynoldsNumber
    * OptimumPipeDiameter
    * FluidVelocity
    * ColebrookWhite
    * PressureDropHazenWilliams
    * TypeOfFlow
"""

import importlib
import pkgutil
import inspect
from pathlib import Path

# Module path and package name
_package_name = __name__
_package_path = Path(__file__).parent

# Public API list for __all__
__all__ = []

# Dynamically discover and import all modules in this package
for module_info in pkgutil.iter_modules([str(_package_path)]):
    module_name = module_info.name
    # Skip private or cache files
    if module_name.startswith("_"):
        continue

    module = importlib.import_module(f"{_package_name}.{module_name}")

    # Find all classes in the module and expose them
    for name, obj in inspect.getmembers(module, inspect.isclass):
        # Only include classes defined in this module (not imported ones)
        if obj.__module__ == module.__name__:
            globals()[name] = obj
            __all__.append(name)
