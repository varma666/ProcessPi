from .base import Component
from processpi.units import *

class Dodecane(Component):
    """
    Represents the properties and constants for Dodecane(C12?H26?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dodecane, which are essential for various process engineering calculations.
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
    name = "Dodecane"
    formula = "C12?H26?"
    molecular_weight = 170.335

    # Critical properties
    _critical_temperature = Temperature(658.0, "K")
    _critical_pressure = Pressure(1.82, "MPa")
    _critical_volume = Volume(0.755, "m3")
    _critical_zc = 0.251
    _critical_acentric_factor = 0.5764

    _density_constants = [0.33267, 0.24664, 658.0, 0.28571]
    _specific_heat_constants = [0.0, 0.0, 3.1015, 0.0, 0.0, 3.6292, 3.9429]
    _viscosity_constants = [-7.8244, 1191.9, -0.49963, 3.96e+23, -10.0]
    _thermal_conductivity_constants = [0.2047, -0.0002326]
    _vapor_pressure_constants = [137.47, 0.0, -16.698, 8.09e-06, 2.0]
    _enthalpy_constants = [7.7337, 0.40681]
