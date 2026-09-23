from .base import Component
from processpi.units import *

class _2Propanol(Component):
    """
    Represents the properties and constants for 2Propanol(C3?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Propanol, which are essential for various process engineering calculations.
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
    name = "2Propanol"
    formula = "C3?H8?O"
    molecular_weight = 60.095

    # Critical properties
    _critical_temperature = Temperature(508.3, "K")
    _critical_pressure = Pressure(4.765, "MPa")
    _critical_volume = Volume(0.222, "m3")
    _critical_zc = 0.25
    _critical_acentric_factor = 0.6544

    _density_constants = [1.1799, 0.2644, 508.3, 0.24653]
    _specific_heat_constants = [0.0, 0.0, 14.745, -0.0144, 0.0, 1.1329, 2.0487]
    _viscosity_constants = [-8.8918, 2357.6, -0.91376]
    _thermal_conductivity_constants = [0.20161, -0.00021529]
    _vapor_pressure_constants = [96.094, 0.0, -10.292, 1.67e-17, 6.0]
    _enthalpy_constants = [7.2542, 0.79137, -0.66092, 0.34223]
