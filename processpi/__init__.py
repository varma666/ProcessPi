# processpi/__init__.py
"""
ProcessPI - Python toolkit for chemical engineering simulations, equipment design, and unit conversions
"""

from importlib.metadata import version, PackageNotFoundError
import time
import sys

# -----------------------
# Version handling
# -----------------------
try:
    __version__ = version("processpi")
except PackageNotFoundError:
    __version__ = "0.1.2"  # fallback for local/dev installs

# -----------------------
# Core submodules import
# -----------------------
from .pipelines.engine import PipelineEngine
from .pipelines.pipelineresults import PipelineResults
from .pipelines.nozzle import Nozzle
from .components import Component

__all__ = [
    "PipelineEngine",
    "PipelineResults",
    "Nozzle",
    "Component",
]

# -----------------------
# Loading animation on import
# -----------------------
def _show_loading_animation():
    """Display a small loading/progress animation in terminal or Colab."""
    if sys.stdout.isatty():  # only display in terminal
        print(f"⚡ Loading ProcessPI v{__version__} ...")
        from tqdm import tqdm
        for _ in tqdm(range(50), desc="Initializing", ncols=70, ascii=True):
            time.sleep(0.02)  # small delay for smooth effect
        print(f"✅ ProcessPI v{__version__} ready!\n")
    else:
        # minimal message in non-terminal environments (like Colab notebooks)
        print(f"⚡ ProcessPI v{__version__} loaded successfully!")

# Call the loading animation automatically on import
_show_loading_animation()
