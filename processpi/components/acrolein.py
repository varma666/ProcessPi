from .base import Component
from processpi.units import *

class Acrolein(Component):
    """
    Represents the properties and constants for Acrolein(C3?H4?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acrolein, which are essential for various process engineering calculations.
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
    name = "Acrolein"
    formula = "C3?H4?O"
    molecular_weight = 56.063

    # Critical properties
    _critical_temperature = Temperature(506.0, "K")
    _critical_pressure = Pressure(5.0, "MPa")
    _critical_volume = Volume(0.197, "m3")
    _critical_zc = 0.234
    _critical_acentric_factor = 0.3198

    _density_constants = [1.3261, 0.26124, 506.0, 0.2489]
    _specific_heat_constants = [0.0, -247.8, 1.0343, 0.0, 0.0, 1.066, 1.5801]
    _viscosity_constants = [-12.032, 867.34, 0.19534]
    _thermal_conductivity_constants = [0.2703, -0.0003764]
    _vapor_pressure_constants = [138.4, 0.0, -19.638, 0.0264, 1.0]
    _enthalpy_constants = [3.8736, 0.29335]
