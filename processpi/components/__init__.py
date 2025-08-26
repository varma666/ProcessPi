"""Initializes the components module.

This module is designed to contain classes representing different components
within a process, such as fluids, equipment, or materials. This __init__.py
file exposes the main component classes for easy access when the module is
imported.

The following classes are exposed for direct use:
    * `Water`: A class representing the properties and behavior of water.
    * `Component`: The abstract base class that all specific component
      classes should inherit from, ensuring a standardized interface.
"""

from .water import Water
from .base import Component

# Defines the public API for this module, making these classes directly
# accessible when the package is imported.
__all__ = ["Water",
           "Component"]
