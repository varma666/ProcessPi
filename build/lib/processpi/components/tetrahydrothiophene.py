from .base import Component
from processpi.units import *

class Tetrahydrothiophene(Component):
    """
    Represents the properties and constants for Tetrahydrothiophene(C4?H8?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Tetrahydrothiophene, which are essential for various process engineering calculations.
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
    name = "Tetrahydrothiophene"
    formula = "C4?H8?S"
    molecular_weight = 88.171

    # Critical properties
    _critical_temperature = Temperature(631.95, "K")
    _critical_pressure = Pressure(5.16, "MPa")
    _critical_volume = Volume(0.249, "m3")
    _critical_zc = 0.245
    _critical_acentric_factor = 0.1996

    _density_constants = [1.1628, 0.28954, 631.95, 0.28674]
    _specific_heat_constants = [0.0, -130.1, 0.6229, 0.0, 0.0, 1.1979, 1.6883]
    _viscosity_constants = [-10.843, 1165.2]
    _thermal_conductivity_constants = [0.20414, -0.00021217]
    _vapor_pressure_constants = [75.881, 0.0, -7.9499, 4.43e-06, 2.0]
    _enthalpy_constants = [5.0642, 0.38904]
