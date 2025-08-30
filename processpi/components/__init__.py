"""
Initializes the components module dynamically.

This module automatically discovers all component classes within the folder
and exposes them for direct import. The base class `Component` is always
included.

Example usage:

    from processpi.components import Water, Ethanol, Acetone
"""

import os
import importlib
import inspect
from pathlib import Path

# -----------------------
# Import the base Component class
# -----------------------
from .base import Component

# Initialize __all__ with the base class
__all__ = ["Component"]

# -----------------------
# Dynamically discover and import component classes
# -----------------------
components_dir = Path(__file__).parent

# List of files to exclude from dynamic import
exclude_files = ["__init__.py", "base.py", "constants.py", "examples.txt"]

for file in components_dir.glob("*.py"):
    if file.name in exclude_files:
        continue

    module_name = file.stem
    module = importlib.import_module(f".{module_name}", package=__name__)

    # Iterate over all classes defined in this module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            globals()[name] = obj
            __all__.append(name)
