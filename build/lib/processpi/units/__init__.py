"""
ProcessPI Units Module
======================

Automatically discovers and exposes all unit variable classes in this package.
The base class `Variable` is always included.

Example:
    from processpi.units import Length, Pressure, Temperature
"""

import importlib
import inspect
from pathlib import Path

# -------------------------------------------------------------------
# Base class import
# -------------------------------------------------------------------
from .base import Variable
from .area import Area
from .density import Density
from .diameter import Diameter
from .dimensionless import Dimensionless
from .heat_flow import HeatFlow
from .heat_flux import HeatFlux
from .heat_of_vaporization import HeatOfVaporization
from .heat_transfer_coefficient import HeatTransferCoefficient
from .length import Length
from .mass_flowrate import MassFlowRate
from .mass import Mass
from .power import Power
from .pressure import Pressure
from .specific_heat import SpecificHeat
from .strings import StringUnit
from .temperature import Temperature
from .thermal_conductivity import ThermalConductivity
from .thermal_resistance import ThermalResistance
from .velocity import Velocity
from .viscosity import Viscosity
from .volume import Volume
from .volumetric_flowrate import VolumetricFlowRate
from .molar_flowrate import MolarFlowRate

__all__ = ["Variable",           
           "Area",
           "Density",
           "Diameter",
           "Dimensionless",
           "HeatFlow",
           "HeatFlux",
           "HeatOfVaporization",
           "HeatTransferCoefficient",
           "Length",
           "MassFlowRate",
           "Mass",
           "Power",
           "Pressure",
           "SpecificHeat",
           "StringUnit",
           "Temperature",
           "ThermalConductivity",
           "ThermalResistance",
           "Velocity",
           "Viscosity",
           "Volume",
           "VolumetricFlowRate",
           "MolarFlowRate"
           ]

