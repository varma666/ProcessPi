from .base import Component
from processpi.units import *

class _2PropylMercaptan(Component):
    """
    Represents the properties and constants for 2Propyl mercaptan(C3?H8?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Propyl mercaptan, which are essential for various process engineering calculations.
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
    name = "2Propyl mercaptan"
    formula = "C3?H8?S"
    molecular_weight = 76.161

    # Critical properties
    _critical_temperature = Temperature(517.0, "K")
    _critical_pressure = Pressure(4.75, "MPa")
    _critical_volume = Volume(0.254, "m3")
    _critical_zc = 0.281
    _critical_acentric_factor = 0.2138

    _density_constants = [1.093, 0.27762, 517.0, 0.29781]
    _specific_heat_constants = [0.0, -117.11, 0.47059, 0.0, 0.0, 1.3126, 1.5505]
    _viscosity_constants = [-5.7244, 638.2, -0.76415]
    _thermal_conductivity_constants = [0.21706, -0.00028952]
    _vapor_pressure_constants = [60.43, 0.0, -5.6572, 2.6e-17, 6.0]
    _enthalpy_constants = [4.2191, 0.41161]
