from .base import Component
from processpi.units import *

class PentanoicAcid(Component):
    """
    Represents the properties and constants for Pentanoic acid(C5?H10?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Pentanoic acid, which are essential for various process engineering calculations.
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
    name = "Pentanoic acid"
    formula = "C5?H10?O2?"
    molecular_weight = 102.132

    # Critical properties
    _critical_temperature = Temperature(639.16, "K")
    _critical_pressure = Pressure(3.63, "MPa")
    _critical_volume = Volume(0.35, "m3")
    _critical_zc = 0.239
    _critical_acentric_factor = 0.7052

    _density_constants = [0.73455, 0.25636, 639.16, 0.25522]
    _specific_heat_constants = [0.0, 28.344, 0.6372, 0.0, 0.0, 1.8827, 2.9228]
    _viscosity_constants = [-37.067, 2856.7, 3.7344]
    _thermal_conductivity_constants = [0.1848, -0.0001434]
    _vapor_pressure_constants = [101.7, 0.0, -10.829, 7.19e-18, 6.0]
    _enthalpy_constants = [7.3197, 1.2093, -1.9114, 1.1591]
