from .base import Component
from processpi.units import *

class Anisole(Component):
    """
    Represents the properties and constants for Anisole(C7?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Anisole, which are essential for various process engineering calculations.
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
    name = "Anisole"
    formula = "C7?H8?O"
    molecular_weight = 108.138

    # Critical properties
    _critical_temperature = Temperature(645.6, "K")
    _critical_pressure = Pressure(4.25, "MPa")
    _critical_volume = Volume(0.337, "m3")
    _critical_zc = 0.267
    _critical_acentric_factor = 0.3502

    _density_constants = [0.77488, 0.26114, 645.6, 0.28234]
    _specific_heat_constants = [0.0, 93.455, 0.23602, 0.0, 0.0, 1.9978, 2.5153]
    _viscosity_constants = [-15.407, 1518.7, 0.60172]
    _thermal_conductivity_constants = [0.23494, -0.00026477]
    _vapor_pressure_constants = [128.06, 0.0, -16.693, 0.0149, 1.0]
    _enthalpy_constants = [5.8662, 0.37127]
