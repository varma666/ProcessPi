from .base import Component
from processpi.units import *

class Thiophene(Component):
    """
    Represents the properties and constants for Thiophene(C4?H4?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Thiophene, which are essential for various process engineering calculations.
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
    name = "Thiophene"
    formula = "C4?H4?S"
    molecular_weight = 84.14

    # Critical properties
    _critical_temperature = Temperature(579.35, "K")
    _critical_pressure = Pressure(5.69, "MPa")
    _critical_volume = Volume(0.219, "m3")
    _critical_zc = 0.259
    _critical_acentric_factor = 0.197

    _density_constants = [1.2874, 0.28194, 579.35, 0.30781]
    _specific_heat_constants = [0.0, 91.725, 0.13243, 0.0, 0.0, 1.1372, 1.3455]
    _viscosity_constants = [-16.671, 1342.5, 0.8388]
    _thermal_conductivity_constants = [0.20571, -0.00020028]
    _vapor_pressure_constants = [93.193, 0.0, -10.738, 8.23e-06, 2.0]
    _enthalpy_constants = [4.5854, 0.38756]
