from .base import Component
from processpi.units import *

class BenzylAlcohol(Component):
    """
    Represents the properties and constants for Benzyl alcohol(C7?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Benzyl alcohol, which are essential for various process engineering calculations.
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
    name = "Benzyl alcohol"
    formula = "C7?H8?O"
    molecular_weight = 108.138

    # Critical properties
    _critical_temperature = Temperature(720.15, "K")
    _critical_pressure = Pressure(4.374, "MPa")
    _critical_volume = Volume(0.382, "m3")
    _critical_zc = 0.279
    _critical_acentric_factor = 0.3631

    _density_constants = [0.59867, 0.22849, 720.15, 0.23567]
    _specific_heat_constants = [0.0, 0.0, -7.77514, 0.00591102, 0.0, 1.8905, 2.7617]
    _viscosity_constants = [-14.152, 2652.0]
    _thermal_conductivity_constants = [0.17847, -6.5843e-05]
    _vapor_pressure_constants = [100.68, 0.0, -10.709, 3.06e-18, 6.0]
    _enthalpy_constants = [8.4762, 0.35251, 0.43853, -0.3026]
