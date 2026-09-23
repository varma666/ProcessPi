from .base import Component
from processpi.units import *

class Octane(Component):
    """
    Represents the properties and constants for Octane(C8?H18?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Octane, which are essential for various process engineering calculations.
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
    name = "Octane"
    formula = "C8?H18?"
    molecular_weight = 114.229

    # Critical properties
    _critical_temperature = Temperature(568.7, "K")
    _critical_pressure = Pressure(2.49, "MPa")
    _critical_volume = Volume(0.486, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.3996

    _density_constants = [0.5266, 0.25693, 568.7, 0.28571]
    _specific_heat_constants = [0.0, -186.63, 0.95891, 0.0, 0.0, 2.2934, 3.4189]
    _viscosity_constants = [-7.556, 881.09, -0.52502, 4.63e+22, -10.0]
    _thermal_conductivity_constants = [0.2156, -0.00029483]
    _vapor_pressure_constants = [96.084, 0.0, -11.003, 7.18e-06, 2.0]
    _enthalpy_constants = [5.518, 0.38467]
