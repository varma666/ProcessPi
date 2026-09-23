from .base import Component
from processpi.units import *

class _2Pentanone(Component):
    """
    Represents the properties and constants for 2Pentanone(C5?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Pentanone, which are essential for various process engineering calculations.
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
    name = "2Pentanone"
    formula = "C5?H10?O"
    molecular_weight = 86.132

    # Critical properties
    _critical_temperature = Temperature(561.08, "K")
    _critical_pressure = Pressure(3.694, "MPa")
    _critical_volume = Volume(0.301, "m3")
    _critical_zc = 0.238
    _critical_acentric_factor = 0.3433

    _density_constants = [0.90411, 0.27207, 561.08, 0.30669]
    _specific_heat_constants = [0.0, -263.86, 0.76808, 0.0, 0.0, 1.7239, 2.038]
    _viscosity_constants = [-11.055, 1005.3, 0.0039301]
    _thermal_conductivity_constants = [0.2161, -0.00024866]
    _vapor_pressure_constants = [84.635, 0.0, -9.3, 6.27e-06, 2.0]
    _enthalpy_constants = [5.174, 0.39422]
