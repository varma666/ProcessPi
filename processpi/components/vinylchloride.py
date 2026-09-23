from .base import Component
from processpi.units import *

class VinylChloride(Component):
    """
    Represents the properties and constants for Vinyl chloride(C2?H3?Cl).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Vinyl chloride, which are essential for various process engineering calculations.
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
    name = "Vinyl chloride"
    formula = "C2?H3?Cl"
    molecular_weight = 62.498

    # Critical properties
    _critical_temperature = Temperature(432.0, "K")
    _critical_pressure = Pressure(5.67, "MPa")
    _critical_volume = Volume(0.179, "m3")
    _critical_zc = 0.283
    _critical_acentric_factor = 0.1001

    _density_constants = [1.5115, 0.2707, 432.0, 0.2716]
    _specific_heat_constants = [0.0, 322.8, 0.0, 0.0, 0.0, 0.5424, 1.188]
    _viscosity_constants = [0.26297, 276.55, -1.7282]
    _thermal_conductivity_constants = [0.2333, -0.00039223]
    _vapor_pressure_constants = [91.432, 0.0, -10.981, 1.43e-05, 2.0]
    _enthalpy_constants = [3.4125, 0.4513]
