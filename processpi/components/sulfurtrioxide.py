from .base import Component
from processpi.units import *

class SulfurTrioxide(Component):
    """
    Represents the properties and constants for Sulfur trioxide(O3?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Sulfur trioxide, which are essential for various process engineering calculations.
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
    name = "Sulfur trioxide"
    formula = "O3?S"
    molecular_weight = 80.063

    # Critical properties
    _critical_temperature = Temperature(490.85, "K")
    _critical_pressure = Pressure(8.21, "MPa")
    _critical_volume = Volume(0.127, "m3")
    _critical_zc = 0.255
    _critical_acentric_factor = 0.424

    _density_constants = [1.4969, 0.19013, 490.85, 0.4359]
    _specific_heat_constants = [0.0, 0.0, 0.0, 0.0, 0.0, 2.5809, 2.5809]
    _viscosity_constants = [-88.793, 6400.7, 10.709]
    _thermal_conductivity_constants = [0.92882, -0.0030803, 2.66e-06]
    _vapor_pressure_constants = [180.99, 0.0, -22.839, 7.24e-17, 6.0]
    _enthalpy_constants = [7.337, 0.5647]
