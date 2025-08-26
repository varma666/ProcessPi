"""
This module contains the core components for the fluid flow simulation engine.
It includes classes for various pipeline elements such as pipes, pumps, and fittings,
as well as the main engine for running simulations and analyzing results.
"""

from .engine import PipelineEngine
from .equipment import Equipment
from .fittings import Fitting
from .network import PipelineNetwork
from .pipelineresults import PipelineResults
from .pipes import Pipe
from .pumps import Pump
from .vessel import Vessel

__all__ = [
    # Main simulation engine class
    "PipelineEngine",

    # Base class for all pipeline equipment
    "Equipment",

    # Represents pipeline fittings like elbows, tees, etc.
    "Fitting",

    # Represents the entire network of interconnected pipes and equipment
    "PipelineNetwork",

    # Stores and manages the results of a simulation run
    "PipelineResults",

    # Represents a single pipe segment
    "Pipe",

    # Represents a pump in the network
    "Pump",

    # Represents a vessel or tank
    "Vessel"
]
