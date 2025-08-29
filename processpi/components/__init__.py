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
from .aceticacid import AceticAcid
from .ethanol import Ethanol
from .methanol import Methanol
from .acetone import Acetone
from .acrylicacid import AcrylicAcid
from .air import Air
from .ammonia import Ammonia
from .benzene import Benzene
from .benzoicacid import BenzoicAcid
from .bromine import Bromine
from .butane import Butane
from .carbondioxide import Carbondioxide
from .carbonmonoxide import CarbonMonoxide
from .carbontetrachloride import CarbonTetrachloride



# Defines the public API for this module, making these classes directly
# accessible when the package is imported.
__all__ = ["Water",
           "Component",
           "AceticAcid",
           "Ethanol",
           "Methanol",
           "Acetone",
           "AcrylicAcid",
           "Air",
           "Ammonia",
           "Benzene",
           "BenzoicAcid",
           "Bromine",
           "Butane",
           "Carbondioxide",
           "CarbonMonoxide",
           "CarbonTetrachloride"]
