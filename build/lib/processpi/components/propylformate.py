from .base import Component
from processpi.units import *

class PropylFormate(Component):
    """
    Represents the properties and constants for Propyl formate(C4?H8?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Propyl formate, which are essential for various process engineering calculations.
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
    name = "Propyl formate"
    formula = "C4?H8?O2?"
    molecular_weight = 88.105

    # Critical properties
    _critical_temperature = Temperature(538.0, "K")
    _critical_pressure = Pressure(4.02, "MPa")
    _critical_volume = Volume(0.285, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.3088

    _density_constants = [0.915, 0.26134, 538.0, 0.28]
    _specific_heat_constants = [0.0, 326.1, 0.0, 0.0, 0.0, 1.7293, 2.0554]
    _viscosity_constants = [-73.735, 2668.2, 10.993, -0.018364, 1.0]
    _thermal_conductivity_constants = [0.2247, -0.000264]
    _vapor_pressure_constants = [104.08, 0.0, -12.348, 9.6e-06, 2.0]
    _enthalpy_constants = [4.9687, 0.4025]
