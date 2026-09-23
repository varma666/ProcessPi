from .base import Component
from processpi.units import *

class Quinone(Component):
    """
    Represents the properties and constants for Quinone(C6?H4?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Quinone, which are essential for various process engineering calculations.
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
    name = "Quinone"
    formula = "C6?H4?O2?"
    molecular_weight = 108.095

    # Critical properties
    _critical_temperature = Temperature(683.0, "K")
    _critical_pressure = Pressure(5.96, "MPa")
    _critical_volume = Volume(0.291, "m3")
    _critical_zc = 0.305
    _critical_acentric_factor = 0.4945

    _density_constants = [0.83228, 0.25385, 683.0, 0.23658]
    _specific_heat_constants = [0.0, 368.33, 0.0, 0.0, 0.0, 1.8904, 2.9738]
    _viscosity_constants = [-14.846, 1829.4, 0.3729]
    _thermal_conductivity_constants = [0.26524, -0.00028676]
    _vapor_pressure_constants = [48.651, 0.0, -3.4453, 1.01e-18, 6.0]
    _enthalpy_constants = [6.49, 0.3112]
