"""
Initializes the units module dynamically.

This module automatically discovers all variable classes within the folder
and exposes them for direct import. The base class `Variable` is always
included.

Example usage:

    from processpi.units import Length, Temperature, Pressure
"""

import importlib
import inspect
from pathlib import Path

# -----------------------
# Import the base Variable class
# -----------------------
from .base import Variable

# Initialize __all__ with the base class
__all__ = ["Variable"]

# -----------------------
# Dynamically discover and import variable classes
# -----------------------
units_dir = Path(__file__).parent

# List of files to exclude from dynamic import
exclude_files = ["__init__.py", "base.py", "example.txt", "strings.py"]

for file in units_dir.glob("*.py"):
    if file.name in exclude_files:
        continue

    module_name = file.stem
    module = importlib.import_module(f".{module_name}", package=__name__)

    # Iterate over all classes defined in this module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            globals()[name] = obj
            __all__.append(name)
