"""
Initializes the main calculations module of ProcessPI.

This module dynamically discovers and loads all calculation submodules and
makes their classes accessible under the processpi.calculations namespace.

Example usage:

    import processpi.calculations as calc
    engine = calc.CalculationEngine()
    water_calc = calc.fluids.PressureDropDarcy(...)
"""

import importlib
import pkgutil
import inspect
from pathlib import Path
import sys
import time

# ------------------------
# Loading animation
# ------------------------
def _show_loading_animation():
    frames = ["⠁","⠂","⠄","⠂"]
    sys.stdout.write(f"⏳ Loading ProcessPI Calculations... ")
    sys.stdout.flush()
    for frame in frames * 2:
        sys.stdout.write(f"\r⏳ Loading ProcessPI Calculations... {frame}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r✅ Calculations module ready!          \n")
    sys.stdout.flush()

_show_loading_animation()

# ------------------------
# Import core classes if any
# ------------------------
from .engine import CalculationEngine  # optional; adjust as needed
from .base import CalculationBase

__all__ = ["CalculationEngine", "CalculationBase"]

# ------------------------
# Dynamically import submodules (e.g., fluids, heat_transfer, etc.)
# ------------------------
package_dir = Path(__file__).parent
package_name = __name__

for finder, name, ispkg in pkgutil.iter_modules([str(package_dir)]):
    # skip private or undesired modules if any
    if name.startswith("_"):
        continue

    full_mod = f"{package_name}.{name}"
    module = importlib.import_module(full_mod)
    globals()[name] = module
    __all__.append(name)

    # Optionally, auto-import module-level classes
    for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass):
        if cls_obj.__module__ == module.__name__:
            globals()[cls_name] = cls_obj
            __all__.append(cls_name)
