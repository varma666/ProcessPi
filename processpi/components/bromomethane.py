from .base import Component
from processpi.units import *

class Bromomethane(Component):
    """
    Represents the properties and constants for Bromomethane(CH3?Br).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Bromomethane, which are essential for various process engineering calculations.
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
    name = "Bromomethane"
    formula = "CH3?Br"
    molecular_weight = 94.939

    # Critical properties
    _critical_temperature = Temperature(467.0, "K")
    _critical_pressure = Pressure(8.0, "MPa")
    _critical_volume = Volume(0.156, "m3")
    _critical_zc = 0.321
    _critical_acentric_factor = 0.1922

    _density_constants = [1.6762, 0.26141, 467.0, 0.28402]
    _specific_heat_constants = [0.0, -596.54, 2.16, -0.0024234, 0.0, 0.7798, 0.787]
    _viscosity_constants = [-8.103, 570.8, -0.32958]
    _thermal_conductivity_constants = [0.1912, -0.000299]
    _vapor_pressure_constants = [72.586, 0.0, -7.9966, 1.16e-05, 2.0]
    _enthalpy_constants = [3.169, 0.3015]
