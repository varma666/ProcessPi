"""
ProcessPI Fluid Mechanics Calculations
======================================

This module loads all calculation classes for fluid mechanics automatically.

Available calculations:
    - PressureDropDarcy
    - PressureDropFanning
    - PumpPower
    - ReynoldsNumber
    - OptimumPipeDiameter
    - FluidVelocity
    - ColebrookWhite
    - PressureDropHazenWilliams
    - TypeOfFlow
"""

import importlib
import pkgutil
import inspect
from pathlib import Path

# Package metadata
__all__ = []
_package_path = Path(__file__).parent
_package_name = __name__

# -------------------------------------------------------------------
# Discover submodules dynamically
# -------------------------------------------------------------------
for _, module_name, _ in pkgutil.iter_modules([str(_package_path)]):
    if module_name.startswith("_"):
        continue
    module = importlib.import_module(f"{_package_name}.{module_name}")

    # Append the module itself to __all__
    globals()[module_name] = module
    __all__.append(module_name)

    # Promote only top-level classes from that module
    for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass):
        if cls_obj.__module__ == module.__name__:
            globals()[cls_name] = cls_obj
            __all__.append(cls_name)
