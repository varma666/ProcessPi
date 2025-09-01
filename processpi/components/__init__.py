"""
ProcessPI Components Module
===========================

Automatically discovers all chemical component classes in this package
and exposes them for direct import.

Example:
    from processpi.components import Water, Ethanol, Acetone
"""

import importlib
import inspect
from pathlib import Path

# -------------------------------------------------------------------
# Base class import
# -------------------------------------------------------------------
from .base import Component

__all__ = ["Component"]

# -------------------------------------------------------------------
# Dynamic discovery of component classes
# -------------------------------------------------------------------
_components_dir = Path(__file__).parent
_excluded = {"__init__.py", "base.py", "constants.py", "examples.txt"}

for file in _components_dir.glob("*.py"):
    if file.name in _excluded:
        continue

    module_name = file.stem
    module = importlib.import_module(f".{module_name}", package=__name__)

    # Promote classes from each module
    for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass):
        if cls_obj.__module__ == module.__name__:
            globals()[cls_name] = cls_obj
            __all__.append(cls_name)
