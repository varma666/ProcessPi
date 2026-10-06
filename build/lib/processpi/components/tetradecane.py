from .base import Component
from processpi.units import *

class Tetradecane(Component):
    """
    Represents the properties and constants for Tetradecane(C14?H30?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Tetradecane, which are essential for various process engineering calculations.
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
    name = "Tetradecane"
    formula = "C14?H30?"
    molecular_weight = 198.388

    # Critical properties
    _critical_temperature = Temperature(693.0, "K")
    _critical_pressure = Pressure(1.57, "MPa")
    _critical_volume = Volume(0.897, "m3")
    _critical_zc = 0.244
    _critical_acentric_factor = 0.643

    _density_constants = [0.27248, 0.24007, 693.0, 0.28571]
    _specific_heat_constants = [0.0, 29.13, 0.86116, 0.0, 0.0, 4.2831, 6.0741]
    _viscosity_constants = [-14.493, 1710.8, 0.4417, 3.09e+28, -12.0]
    _thermal_conductivity_constants = [0.20293, -0.00021798]
    _vapor_pressure_constants = [140.47, 0.0, -16.859, 6.59e-06, 2.0]
    _enthalpy_constants = [9.0539, 0.44467]
