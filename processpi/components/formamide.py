from .base import Component
from processpi.units import *

class Formamide(Component):
    """
    Represents the properties and constants for Formamide(CH3?NO).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Formamide, which are essential for various process engineering calculations.
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
    name = "Formamide"
    formula = "CH3?NO"
    molecular_weight = 45.041

    # Critical properties
    _critical_temperature = Temperature(771.0, "K")
    _critical_pressure = Pressure(7.8, "MPa")
    _critical_volume = Volume(0.163, "m3")
    _critical_zc = 0.198
    _critical_acentric_factor = 0.4124

    _density_constants = [1.2486, 0.20352, 771.0, 0.25178]
    _specific_heat_constants = [0.0, 150.6, 0.0, 0.0, 0.0, 1.0738, 1.3765]
    _viscosity_constants = [40.153, -912.39, -7.5664, 1.69e+24, -10.0]
    _thermal_conductivity_constants = [0.3847, -0.0001065]
    _vapor_pressure_constants = [100.3, 0.0, -10.946, 3.85e-06, 2.0]
    _enthalpy_constants = [7.358, 0.3564]
