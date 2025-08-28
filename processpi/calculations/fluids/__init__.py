"""Initializes the Process PI calculation engine module.

This module provides a collection of classes for performing calculations related to fluid mechanics and process engineering. The included classes handle key engineering tasks such as calculating pressure drop, pump power, fluid velocity, and determining flow characteristics.

**Classes:**
    * `PressureDropDarcy`: Calculates the pressure drop in a pipe using the Darcy-Weisbach equation.
    * `PressureDropFanning`: Calculates the pressure drop using the Fanning friction factor.
    * `PumpPower`: Determines the required pump power for a fluid system.
    * `ReynoldsNumber`: Computes the Reynolds number to characterize the fluid flow regime.
    * `OptimumPipeDiameter`: Calculates the most efficient pipe diameter for a given flow.
    * `FluidVelocity`: Determines the velocity of the fluid within a pipe.
    * `ColebrookWhite`: Calculates the friction factor using the Colebrook-White equation for turbulent flow.
    * `TypeOfFlow`: Classifies the fluid flow as laminar or turbulent based on the Reynolds number.
"""

# Import public classes from sub-modules to make them directly available under the package namespace.
from .pressure_drop_darcy import PressureDropDarcy
from .pressure_drop_fanning import PressureDropFanning
from .pump_power import PumpPower
from .reynolds_number import ReynoldsNumber
from .optimium_pipe_dia import OptimumPipeDiameter
from .velocity import FluidVelocity
from .friction_factor_colebrookwhite import ColebrookWhite
from .pressure_drop_hazen_williams import PressureDropHazenWilliams
from .flow_type import TypeOfFlow

# Define the public API of the module. This list specifies which objects are accessible
# when a user imports the package using `from process_pi_engine import *`.
__all__ = ["PressureDropDarcy",
           "PressureDropFanning", 
           "PumpPower", 
           "ReynoldsNumber", 
           "OptimumPipeDiameter", 
           "FluidVelocity", 
           "ColebrookWhite", 
           "PressureDropHazenWilliams", 
           "TypeOfFlow"]
