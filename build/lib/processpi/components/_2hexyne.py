from .base import Component
from processpi.units import *

class _2Hexyne(Component):
    """
    Represents the properties and constants for 2Hexyne(C6?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Hexyne, which are essential for various process engineering calculations.
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
    name = "2Hexyne"
    formula = "C6?H10?"
    molecular_weight = 82.144

    # Critical properties
    _critical_temperature = Temperature(549.0, "K")
    _critical_pressure = Pressure(3.53, "MPa")
    _critical_volume = Volume(0.331, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.2214

    _density_constants = [0.76277, 0.25248, 549.0, 0.31611]
    _specific_heat_constants = [0.0, 0.0, 0.0, 0.0, 0.0, 1.711, 1.8576]
    _viscosity_constants = [-3.7464, 624.2, -1.084]
    _thermal_conductivity_constants = [0.2119, -0.00027048]
    _vapor_pressure_constants = [123.71, 0.0, -16.451, 0.0165, 1.0]
    _enthalpy_constants = [4.911, 0.4392]
