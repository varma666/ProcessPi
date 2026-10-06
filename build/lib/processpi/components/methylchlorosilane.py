from .base import Component
from processpi.units import *

class Methylchlorosilane(Component):
    """
    Represents the properties and constants for Methylchlorosilane(CH5?ClSi).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylchlorosilane, which are essential for various process engineering calculations.
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
    name = "Methylchlorosilane"
    formula = "CH5?ClSi"
    molecular_weight = 80.589

    # Critical properties
    _critical_temperature = Temperature(442.0, "K")
    _critical_pressure = Pressure(4.17, "MPa")
    _critical_volume = Volume(0.246, "m3")
    _critical_zc = 0.279
    _critical_acentric_factor = 0.2252

    _density_constants = [1.0674, 0.26257, 442.0, 0.26569]
    _specific_heat_constants = [0.0, 338.4, 0.0, 0.0, 0.0, 1.3233, 1.5771]
    _viscosity_constants = [-12.002, 1009.7]
    _thermal_conductivity_constants = [0.24683, -0.00038854]
    _vapor_pressure_constants = [95.984, 0.0, -11.829, 1.81e-05, 2.0]
    _enthalpy_constants = [3.2835, 0.33116]
