from .base import Component
from processpi.units import *

class Benzamide(Component):
    """
    Represents the properties and constants for Benzamide(C7?H7?NO).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Benzamide, which are essential for various process engineering calculations.
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
    name = "Benzamide"
    formula = "C7?H7?NO"
    molecular_weight = 121.137

    # Critical properties
    _critical_temperature = Temperature(824.0, "K")
    _critical_pressure = Pressure(5.05, "MPa")
    _critical_volume = Volume(0.346, "m3")
    _critical_zc = 0.255
    _critical_acentric_factor = 0.5585

    _density_constants = [0.7371, 0.25487, 824.0, 0.28571]
    _specific_heat_constants = [0.0, 260.66, 0.0, 0.0, 0.0, 2.6649, 3.0823]
    _viscosity_constants = [-12.632, 2668.2]
    _thermal_conductivity_constants = [0.28485, -0.00025225]
    _vapor_pressure_constants = [85.474, 0.0, -8.3348, 1.29e-18, 6.0]
    _enthalpy_constants = [8.7809, 0.1933, 0.30877, -0.14162]
