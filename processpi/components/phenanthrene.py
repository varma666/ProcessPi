from .base import Component
from processpi.units import *

class Phenanthrene(Component):
    """
    Represents the properties and constants for Phenanthrene(C14?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Phenanthrene, which are essential for various process engineering calculations.
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
    name = "Phenanthrene"
    formula = "C14?H10?"
    molecular_weight = 178.229

    # Critical properties
    _critical_temperature = Temperature(869.0, "K")
    _critical_pressure = Pressure(2.9, "MPa")
    _critical_volume = Volume(0.554, "m3")
    _critical_zc = 0.222
    _critical_acentric_factor = 0.4707

    _density_constants = [0.45554, 0.2523, 869.0, 0.24841]
    _specific_heat_constants = [0.0, 527.03, 0.0, 0.0, 0.0, 2.9963, 3.6688]
    _viscosity_constants = [-22.472, 2566.9, 1.5749]
    _thermal_conductivity_constants = [0.13753, -2.5247e-05]
    _vapor_pressure_constants = [72.958, 0.0, -6.7902, 1.09e-18, 6.0]
    _enthalpy_constants = [8.3482, 0.33172]
