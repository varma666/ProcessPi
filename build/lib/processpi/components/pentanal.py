from .base import Component
from processpi.units import *

class Pentanal(Component):
    """
    Represents the properties and constants for Pentanal(C5?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Pentanal, which are essential for various process engineering calculations.
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
    name = "Pentanal"
    formula = "C5?H10?O"
    molecular_weight = 86.132

    # Critical properties
    _critical_temperature = Temperature(566.1, "K")
    _critical_pressure = Pressure(3.97, "MPa")
    _critical_volume = Volume(0.313, "m3")
    _critical_zc = 0.264
    _critical_acentric_factor = 0.3472

    _density_constants = [0.83871, 0.26252, 566.1, 0.29444]
    _specific_heat_constants = [0.0, 257.78, 0.0, 0.0, 0.0, 1.6361, 2.0901]
    _viscosity_constants = [-10.846, 980.01, -0.0054565]
    _thermal_conductivity_constants = [0.22697, -0.00033227, 1.18e-07]
    _vapor_pressure_constants = [149.58, 0.0, -20.697, 0.0221, 1.0]
    _enthalpy_constants = [5.1478, 0.37541]
