"""
ProcessPI Calculations Module
=============================

This module provides core calculation classes and dynamically
loads all available calculation submodules under `processpi.calculations`.

Example:
    import processpi.calculations as calc

    engine = calc.CalculationEngine()
    water_dp = calc.fluids.PressureDropDarcy(...)
"""

import sys
import time
import importlib
import pkgutil
from pathlib import Path

# -------------------------------------------------------------------
# Optional: Loading Animation
# -------------------------------------------------------------------
def _show_loading():
    if not sys.stdout.isatty():
        return
    frames = "⠁⠂⠄⠂"
    sys.stdout.write("⏳ Loading ProcessPI Calculations... ")
    sys.stdout.flush()
    for frame in frames * 2:
        sys.stdout.write(f"\r⏳ Loading ProcessPI Calculations... {frame}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r✅ Calculations module ready!          \n")

_show_loading()

# -------------------------------------------------------------------
# Core classes (explicit for static analyzers)
# -------------------------------------------------------------------
from .engine import CalculationEngine
from .base import CalculationBase

__all__ = ["CalculationEngine", "CalculationBase"]

# -------------------------------------------------------------------
# Dynamically import submodules, no class injection
# -------------------------------------------------------------------
_package_dir = Path(__file__).parent
for _, name, is_pkg in pkgutil.iter_modules([str(_package_dir)]):
    if name.startswith("_") or name in ["engine", "base"]:
        continue
    module = importlib.import_module(f"{__name__}.{name}")
    globals()[name] = module
    __all__.append(name)
