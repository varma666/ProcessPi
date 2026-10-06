from .base import Component
from processpi.units import *

class _14Dioxane(Component):
    """
    Represents the properties and constants for 14Dioxane(C4?H8?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 14Dioxane, which are essential for various process engineering calculations.
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
    name = "14Dioxane"
    formula = "C4?H8?O2?"
    molecular_weight = 88.105

    # Critical properties
    _critical_temperature = Temperature(587.0, "K")
    _critical_pressure = Pressure(5.208, "MPa")
    _critical_volume = Volume(0.238, "m3")
    _critical_zc = 0.254
    _critical_acentric_factor = 0.2793

    _density_constants = [1.1819, 0.2813, 587.0, 0.3047]
    _specific_heat_constants = [0.0, 0.0, 9.6124, 0.0, 0.0, 1.5306, 2.2277]
    _viscosity_constants = [-46.166, 3086.2, 5.104]
    _thermal_conductivity_constants = [0.3027, -0.0004827]
    _vapor_pressure_constants = [44.494, 0.0, -3.1287, 2.89e-18, 6.0]
    _enthalpy_constants = [5.051, 0.3791]
