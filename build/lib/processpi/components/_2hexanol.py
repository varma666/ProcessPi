from .base import Component
from processpi.units import *

class _2Hexanol(Component):
    """
    Represents the properties and constants for 2Hexanol(C6?H14?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Hexanol, which are essential for various process engineering calculations.
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
    name = "2Hexanol"
    formula = "C6?H14?O"
    molecular_weight = 102.175

    # Critical properties
    _critical_temperature = Temperature(585.3, "K")
    _critical_pressure = Pressure(3.311, "MPa")
    _critical_volume = Volume(0.385, "m3")
    _critical_zc = 0.262
    _critical_acentric_factor = 0.5574

    _density_constants = [0.67393, 0.25948, 585.3, 0.26552]
    _specific_heat_constants = [0.0, 0.0, 3.35185, 0.0, 0.0, 2.0394, 8.1124]
    _viscosity_constants = [-82.705, 7404.9, 6.4721, 1.5016, 0.41014]
    _thermal_conductivity_constants = [0.21391, -0.00026042]
    _vapor_pressure_constants = [109.42, 0.0, -12.051, 2.61e-46, 16.0]
    _enthalpy_constants = [11.55, 2.2877, -3.6724, 2.1326]
