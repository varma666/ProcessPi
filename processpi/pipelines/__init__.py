"""
ProcessPI Pipelines Module
==========================

Provides core components for the fluid flow simulation engine, including:
- Pipeline elements: Pipe, Pump, Vessel, Junction
- Main engine: PipelineEngine for simulations and analysis

Example:
    from processpi.pipelines import PipelineEngine, Pipe, Pump
"""

import importlib
import inspect
from pathlib import Path

# -------------------------------------------------------------------
# Public API initialization
# -------------------------------------------------------------------
__all__ = []

# Directory of this package
_pipelines_dir = Path(__file__).parent

# Files to skip for dynamic imports
_excluded = {"__init__.py", "todo.md", "processpi_pipeline_engine_features.md"}

# -------------------------------------------------------------------
# Dynamic discovery of pipeline components
# -------------------------------------------------------------------
for file in _pipelines_dir.glob("*.py"):
    if file.name in _excluded:
        continue

    module_name = file.stem
    module = importlib.import_module(f".{module_name}", package=__name__)

    # Promote all top-level classes in the module
    for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass):
        if cls_obj.__module__ == module.__name__:
            globals()[cls_name] = cls_obj
            __all__.append(cls_name)
