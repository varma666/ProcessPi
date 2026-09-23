from .base import Component
from processpi.units import *

class Nonane(Component):
    """
    Represents the properties and constants for Nonane(C9?H20?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nonane, which are essential for various process engineering calculations.
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
    name = "Nonane"
    formula = "C9?H20?"
    molecular_weight = 128.255

    # Critical properties
    _critical_temperature = Temperature(594.6, "K")
    _critical_pressure = Pressure(2.29, "MPa")
    _critical_volume = Volume(0.551, "m3")
    _critical_zc = 0.255
    _critical_acentric_factor = 0.4435

    _density_constants = [0.46321, 0.25444, 594.6, 0.28571]
    _specific_heat_constants = [0.0, 0.0, 2.7101, 0.0, 0.0, 2.6348, 2.989]
    _viscosity_constants = [-68.54, 3165.3, 9.0919, -1.3519e-05, 2.0]
    _thermal_conductivity_constants = [0.209, -0.000264]
    _vapor_pressure_constants = [109.35, 0.0, -12.882, 7.85e-06, 2.0]
    _enthalpy_constants = [6.037, 0.38522]
