from .base import Component
from processpi.units import *

class EthylPropionate(Component):
    """
    Represents the properties and constants for Ethyl propionate(C5?H10?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethyl propionate, which are essential for various process engineering calculations.
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
    name = "Ethyl propionate"
    formula = "C5?H10?O2?"
    molecular_weight = 102.132

    # Critical properties
    _critical_temperature = Temperature(546.0, "K")
    _critical_pressure = Pressure(3.362, "MPa")
    _critical_volume = Volume(0.345, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.3944

    _density_constants = [0.7405, 0.25563, 546.0, 0.2795]
    _specific_heat_constants = [0.0, 400.1, 0.0, 0.0, 0.0, 1.9562, 2.4037]
    _viscosity_constants = [-8.9215, 950.8, -0.32687]
    _thermal_conductivity_constants = [0.2137, -0.0002515]
    _vapor_pressure_constants = [105.64, 0.0, -12.477, 9e-06, 2.0]
    _enthalpy_constants = [5.3325, 0.401]
