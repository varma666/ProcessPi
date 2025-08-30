"""
Process PI - Core Calculations Module
=====================================

This module initializes the calculation engine of Process PI. It dynamically:
- Loads the current version from the package metadata
- Imports CalculationEngine and CalculationBase for direct use
- Auto-discovers all submodules and their classes for convenience
- Displays a sleek loading animation during initialization

Users can simply:
    >>> import processpi.calculations
    >>> engine = processpi.calculations.CalculationEngine()
"""

import importlib
import importlib.metadata
import os
import pkgutil
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------
# Dynamic Version
# ---------------------------------------------------------------------
try:
    __version__ = importlib.metadata.version("processpi")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"

# ---------------------------------------------------------------------
# Loading animation
# ---------------------------------------------------------------------
def _show_loading_animation():
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    sys.stdout.write(f"🔄 Initializing Process PI Calculations v{__version__} ")
    sys.stdout.flush()
    for frame in animation:
        sys.stdout.write(f"\r🔄 Initializing Process PI Calculations v{__version__} {frame}")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write("\r✅ Process PI Calculations ready!            \n")
    sys.stdout.flush()

_show_loading_animation()

# ---------------------------------------------------------------------
# Core classes import
# ---------------------------------------------------------------------
from .engine import CalculationEngine
from .base import CalculationBase

# Public API
__all__ = ["CalculationEngine", "CalculationBase"]

# ---------------------------------------------------------------------
# Auto-discover and import submodules and their classes
# ---------------------------------------------------------------------
_current_dir = Path(__file__).parent

for finder, module_name, ispkg in pkgutil.iter_modules([str(_current_dir)]):
    if module_name not in {"engine", "base", "__init__"}:
        full_module = f"{__name__}.{module_name}"
        try:
            module = importlib.import_module(full_module)
            globals()[module_name] = module
            __all__.append(module_name)
        except Exception as e:
            print(f"⚠️ Failed to auto-import module '{module_name}': {e}")
