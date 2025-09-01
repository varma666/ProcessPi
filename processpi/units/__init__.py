"""
ProcessPI Units Module
======================

Automatically discovers and exposes all unit variable classes in this package.
The base class `Variable` is always included.

Example:
    from processpi.units import Length, Pressure, Temperature
"""

import importlib
import inspect
from pathlib import Path

# -------------------------------------------------------------------
# Base class import
# -------------------------------------------------------------------
from .base import Variable

__all__ = ["Variable"]

# -------------------------------------------------------------------
# Dynamic discovery of unit classes
# -------------------------------------------------------------------
_units_dir = Path(__file__).parent
_excluded = {"__init__.py", "base.py", "example.txt", "strings.py"}

for file in _units_dir.glob("*.py"):
    if file.name in _excluded:
        continue

    module_name = file.stem
    module = importlib.import_module(f".{module_name}", package=__name__)

    # Promote top-level classes to namespace
    for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass):
        if cls_obj.__module__ == module.__name__:
            globals()[cls_name] = cls_obj
            __all__.append(cls_name)
