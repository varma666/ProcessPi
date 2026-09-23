from .base import Component
from processpi.units import *

class SulfurHexafluoride(Component):
    """
    Represents the properties and constants for Sulfur hexafluoride(F6?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Sulfur hexafluoride, which are essential for various process engineering calculations.
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
    name = "Sulfur hexafluoride"
    formula = "F6?S"
    molecular_weight = 146.055

    # Critical properties
    _critical_temperature = Temperature(318.69, "K")
    _critical_pressure = Pressure(3.76, "MPa")
    _critical_volume = Volume(0.19852, "m3")
    _critical_zc = 0.282
    _critical_acentric_factor = 0.2151

    _density_constants = [1.3587, 0.2701, 318.69, 0.2921]
    _specific_heat_constants = [0.0, 0.0, 0.0, 0.0, 0.0, 1.195, 1.195]
    _viscosity_constants = [3.8305, 41.21, -2.1342]
    _thermal_conductivity_constants = [0.2544, -0.0006595]
    _vapor_pressure_constants = [29.16, 0.0, -1.1342, 0.0, 0.0]
    _enthalpy_constants = [2.571, 0.383]
