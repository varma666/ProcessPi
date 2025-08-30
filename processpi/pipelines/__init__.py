"""
Initializes the pipelines module dynamically.

This module contains the core components for the fluid flow simulation engine,
including classes for various pipeline elements such as pipes, pumps, vessels,
and the main engine for running simulations and analyzing results.

Example usage:

    from processpi.pipelines import PipelineEngine, Pump, Pipe
"""

import importlib
import inspect
from pathlib import Path

# -----------------------
# Initialize public API
# -----------------------
__all__ = []

pipelines_dir = Path(__file__).parent

# Files to exclude from dynamic import
exclude_files = ["__init__.py", "todo.md", "processpi_pipeline_engine_features.md"]

for file in pipelines_dir.glob("*.py"):
    if file.name in exclude_files:
        continue

    module_name = file.stem
    module = importlib.import_module(f".{module_name}", package=__name__)

    # Iterate over all classes defined in the module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            globals()[name] = obj
            __all__.append(name)
