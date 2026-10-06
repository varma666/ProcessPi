from .base import Component
from processpi.units import *

class Nitromethane(Component):
    """
    Represents the properties and constants for Nitromethane(CH3?NO2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nitromethane, which are essential for various process engineering calculations.
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
    name = "Nitromethane"
    formula = "CH3?NO2?"
    molecular_weight = 61.04

    # Critical properties
    _critical_temperature = Temperature(588.15, "K")
    _critical_pressure = Pressure(6.31, "MPa")
    _critical_volume = Volume(0.173, "m3")
    _critical_zc = 0.223
    _critical_acentric_factor = 0.348

    _density_constants = [1.3728, 0.23793, 588.15, 0.29601]
    _specific_heat_constants = [0.0, -135.3, 0.345, 0.0, 0.0, 1.0382, 1.2949]
    _viscosity_constants = [-9.5556, 981.64, -0.19453]
    _thermal_conductivity_constants = [0.3276, -0.000405]
    _vapor_pressure_constants = [57.278, 0.0, -4.9821, 1.22e-17, 6.0]
    _enthalpy_constants = [4.7417, 0.3062]
