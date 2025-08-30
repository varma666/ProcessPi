# processpi/__init__.py
"""
ProcessPI - Python toolkit for chemical engineering simulations, equipment design, and unit conversions
"""

from importlib.metadata import version, PackageNotFoundError

# -----------------------
# Version handling
# -----------------------
try:
    # Fetch version from installed package metadata (PyPI wheel)
    __version__ = version("processpi")
except PackageNotFoundError:
    # Fallback for local development or editable installs
    __version__ = "0.1.2"

# -----------------------
# Core submodules import
# -----------------------
# Adjust these imports based on your package structure
# e.g., processpi/pipelines, processpi/components, processpi/utils, etc.

from .pipelines.engine import PipelineEngine
from .pipelines.pipelineresults import PipelineResults
from .pipelines.nozzle import Nozzle
from .components import Component

# Optional: expose frequently used functions/classes at top-level
__all__ = [
    "PipelineEngine",
    "PipelineResults",
    "Nozzle",
    "Component",
]

# -----------------------
# Optional: initialization message or logging
# -----------------------
def _welcome_message():
    print(f"⚡ ProcessPI v{__version__} loaded successfully!")

# Uncomment the following line if you want a small message whenever imported
# _welcome_message()
