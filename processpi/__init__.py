"""
ProcessPI: Chemical & Process Engineering Tools
==============================================

ProcessPI is a Python library for process engineers to perform calculations,
simulate fluid systems, and design equipment.

Features:
---------
- Fluid mechanics and hydraulic calculations
- Pipeline network simulation and visualization
- Chemical and physical properties management
- Unit handling and conversions
"""

import os
import sys
import time
import importlib
import pkgutil
from pathlib import Path

# -------------------------------------------------------------------
# Dynamic Version Handling
# -------------------------------------------------------------------
try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version("processpi")
except PackageNotFoundError:
    __version__ = "0.1.0"  # fallback version for dev environments

__all__ = []

# -------------------------------------------------------------------
# Sleek Loading Animation
# -------------------------------------------------------------------
def _loading_animation(text="Initializing ProcessPI"):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    for i in range(20):
        sys.stdout.write(f"\r{text} {frames[i % len(frames)]}")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write("\r✅ ProcessPI Ready!             \n")

# Only show animation in interactive sessions (terminal/Colab)
if sys.stdout.isatty() or "COLAB_GPU" in os.environ:
    _loading_animation()

# -------------------------------------------------------------------
# Import Core Submodules
# -------------------------------------------------------------------
from . import calculations, pipelines, units, components

__all__.extend(["calculations", "pipelines", "units", "components"])

# -------------------------------------------------------------------
# Dynamic Discovery & Import of Component Classes
# -------------------------------------------------------------------
_components_dir = Path(__file__).parent / "components"

for _, module_name, is_pkg in pkgutil.iter_modules([str(_components_dir)]):
    if not is_pkg:  # Import each component module dynamically
        module = importlib.import_module(f"{__name__}.components.{module_name}")
        globals()[module_name] = module
        __all__.append(module_name)

# Automatically collect all classes from components
for mod in list(__all__):
    module_obj = globals().get(mod)
    if module_obj and hasattr(module_obj, "__dict__"):
        for name, obj in module_obj.__dict__.items():
            if isinstance(obj, type):  # only classes
                globals()[name] = obj
                __all__.append(name)

# -------------------------------------------------------------------
# Friendly Banner for Interactive Users
# -------------------------------------------------------------------
if sys.stdout.isatty() or "COLAB_GPU" in os.environ:
    print(f"📦 ProcessPI v{__version__} | Chemical & Process Engineering Tools Loaded!\n")
