"""Initializes the main calculations module.

This module serves as the core of the Process PI calculation engine,
providing the base classes and the main engine for performing various
engineering and fluid dynamics calculations.

The following classes are exposed for direct use:
    * `CalculationEngine`: The central class for orchestrating and running
      calculations by dynamically selecting and executing the appropriate
      calculation class based on input.
    * `CalculationBase`: The abstract base class that all specific
      calculation classes should inherit from, ensuring a standardized
      interface with methods like `validate_inputs` and `calculate`.
"""

from .engine import CalculationEngine
from .base import CalculationBase

# Defines the public API for this module, making these classes directly
# accessible when the package is imported.
__all__ = ["CalculationEngine", "CalculationBase"]
