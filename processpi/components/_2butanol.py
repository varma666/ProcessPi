from .base import Component
from processpi.units import *

class _2Butanol(Component):
    """
    Represents the properties and constants for 2Butanol(C4?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Butanol, which are essential for various process engineering calculations.
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
    name = "2Butanol"
    formula = "C4?H10?O"
    molecular_weight = 74.122

    # Critical properties
    _critical_temperature = Temperature(535.9, "K")
    _critical_pressure = Pressure(4.188, "MPa")
    _critical_volume = Volume(0.27, "m3")
    _critical_zc = 0.254
    _critical_acentric_factor = 0.5692

    _density_constants = [0.9682, 0.26244, 535.9, 0.26749]
    _specific_heat_constants = [0.0, 0.0, 13.828, -0.0135, 0.0, 1.3485, 2.719]
    _viscosity_constants = [-16.323, 3141.7]
    _thermal_conductivity_constants = [0.22787, -0.00030727]
    _vapor_pressure_constants = [114.68, 0.0, -12.963, 1.87e-17, 6.0]
    _enthalpy_constants = [7.9227, 0.58361, 0.02016, -0.08654]
