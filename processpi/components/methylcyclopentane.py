from .base import Component
from processpi.units import *

class Methylcyclopentane(Component):
    """
    Represents the properties and constants for Methylcyclopentane(C6?H12?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylcyclopentane, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    **Properties:**
    - `name`: The common name of the compound.
    - `formula`: The chemical formula.
    - `molecular_weight`: The molar mass in g/mol.
    - `_critical_temperature`: The critical temperature, above which a substance
      cannot exist as a liquid, regardless of pressure.
    - `_critical_pressure`: The critical pressure, the vapor pressure at the
      critical temperature.
    - `_critical_volume`: The critical volume per kmole.
    - `_critical_zc`: The critical compressibility factor.
    - `_critical_acentric_factor`: The acentric factor, a measure of the
      non-sphericity of the molecule.
    - `_density_constants`: Constants for calculating density as a function of temperature.
    - `_specific_heat_constants`: Constants for calculating specific heat capacity as a
      function of temperature.
    - `_viscosity_constants`: Constants for calculating viscosity as a function of
      temperature.
    - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity
      as a function of temperature.
    - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a
      function of temperature using the Antoine equation or similar models.
    - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature.
    """
    name = "Methylcyclopentane"
    formula = "C6?H12?"
    molecular_weight = 84.159

    # Critical properties
    _critical_temperature = Temperature(532.7, "K")
    _critical_pressure = Pressure(3.79, "MPa")
    _critical_volume = Volume(0.319, "m3")
    _critical_zc = 0.273
    _critical_acentric_factor = 0.2288

    _density_constants = [0.84758, 0.27037, 532.7, 0.28258]
    _specific_heat_constants = [0.0, -490.0, 2.1383, -0.0015585, 0.0, 1.2492, 1.8682]
    _viscosity_constants = [-1.8553, 612.62, -1.3774]
    _thermal_conductivity_constants = [0.1929, -0.0002492]
    _vapor_pressure_constants = [55.368, 0.0, -5.0136, 3.22e-06, 2.0]
    _enthalpy_constants = [4.3595, 0.38507]
