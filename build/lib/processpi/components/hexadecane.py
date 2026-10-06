from .base import Component
from processpi.units import *

class Hexadecane(Component):
    """
    Represents the properties and constants for Hexadecane(C16?H34?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hexadecane, which are essential for various process engineering calculations.
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
    name = "Hexadecane"
    formula = "C16?H34?"
    molecular_weight = 226.441

    # Critical properties
    _critical_temperature = Temperature(723.0, "K")
    _critical_pressure = Pressure(1.4, "MPa")
    _critical_volume = Volume(1.04, "m3")
    _critical_zc = 0.243
    _critical_acentric_factor = 0.7174

    _density_constants = [0.23289, 0.23659, 723.0, 0.28571]
    _specific_heat_constants = [0.0, 231.47, 0.68632, 0.0, 0.0, 4.9602, 7.1521]
    _viscosity_constants = [-20.182, 2203.5, 1.2289]
    _thermal_conductivity_constants = [0.20749, -0.00021917]
    _vapor_pressure_constants = [156.06, 0.0, -18.941, 6.82e-06, 2.0]
    _enthalpy_constants = [10.156, 0.45726]
