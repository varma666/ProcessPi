from .base import Component
from processpi.units import *

class HexylMercaptan(Component):
    """
    Represents the properties and constants for Hexyl mercaptan(C6?H14?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hexyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Hexyl mercaptan"
    formula = "C6?H14?S"
    molecular_weight = 118.24

    # Critical properties
    _critical_temperature = Temperature(623.0, "K")
    _critical_pressure = Pressure(3.08, "MPa")
    _critical_volume = Volume(0.412, "m3")
    _critical_zc = 0.245
    _critical_acentric_factor = 0.3681

    _density_constants = [0.66372, 0.27345, 623.0, 0.29185]
    _specific_heat_constants = [0.0, 0.0, 3.3885, -0.002762, 0.0, 2.1495, 2.7639]
    _viscosity_constants = [-10.073, 1123.3, -0.16515]
    _thermal_conductivity_constants = [0.2058, -0.0002324]
    _vapor_pressure_constants = [68.467, 0.0, -6.5456, 7.76e-18, 6.0]
    _enthalpy_constants = [5.8422, 0.38704]
