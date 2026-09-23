from .base import Component
from processpi.units import *

class Mcresol(Component):
    """
    Represents the properties and constants for mCresol(C7?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for mCresol, which are essential for various process engineering calculations.
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
    name = "mCresol"
    formula = "C7?H8?O"
    molecular_weight = 108.138

    # Critical properties
    _critical_temperature = Temperature(705.85, "K")
    _critical_pressure = Pressure(4.56, "MPa")
    _critical_volume = Volume(0.312, "m3")
    _critical_zc = 0.242
    _critical_acentric_factor = 0.448

    _density_constants = [0.9061, 0.28268, 705.85, 0.2707]
    _specific_heat_constants = [0.0, 0.0, -7.4202, 0.0060467, 0.0, 2.1895, 2.5578]
    _viscosity_constants = [59.686, -3517.9, -9.838, 9030000000000.0, -5.0]
    _thermal_conductivity_constants = [0.18241, -0.00011109]
    _vapor_pressure_constants = [95.403, 0.0, -10.004, 4.3e-18, 6.0]
    _enthalpy_constants = [8.0082, 0.45314]
