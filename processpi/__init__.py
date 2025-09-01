"""
ProcessPI: Chemical & Process Engineering Tools
==============================================

A Python library for process engineers to:
- Perform fluid mechanics and hydraulic calculations
- Simulate and visualize pipeline networks
- Manage chemical and physical properties
- Handle engineering units and conversions
"""

import sys
import os
import time
from importlib.metadata import version, PackageNotFoundError

# -------------------------------------------------------------------
# Version Handling
# -------------------------------------------------------------------
try:
    __version__ = version("processpi")
except PackageNotFoundError:
    __version__ = "0.1.0"

# -------------------------------------------------------------------
# Submodules (explicit imports for static analyzers)
# -------------------------------------------------------------------
from . import calculations
from . import pipelines
from . import units
from . import components

__all__ = ["calculations", "pipelines", "units", "components"]

# -------------------------------------------------------------------
# Loading animation (only for interactive sessions)
# -------------------------------------------------------------------
def _show_loading(text="Initializing ProcessPI"):
    if not (sys.stdout.isatty() or "COLAB_GPU" in os.environ):
        return
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for i in range(20):
        sys.stdout.write(f"\r{text} {frames[i % len(frames)]}")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write("\r✅ ProcessPI Ready!\n")

_show_loading()

# -------------------------------------------------------------------
# Friendly banner for interactive use
# -------------------------------------------------------------------
if sys.stdout.isatty() or "COLAB_GPU" in os.environ:
    print(f"📦 ProcessPI v{__version__} | Chemical & Process Engineering Tools Loaded!\n")
