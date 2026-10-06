from .base import Component
from processpi.units import *

class Ethylcyclopentane(Component):
    """
    Represents the properties and constants for Ethylcyclopentane(C7?H14?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylcyclopentane, which are essential for various process engineering calculations.
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
    name = "Ethylcyclopentane"
    formula = "C7?H14?"
    molecular_weight = 98.186

    # Critical properties
    _critical_temperature = Temperature(569.5, "K")
    _critical_pressure = Pressure(3.4, "MPa")
    _critical_volume = Volume(0.375, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.2701

    _density_constants = [0.71751, 0.26903, 569.5, 0.27733]
    _specific_heat_constants = [0.0, -518.35, 2.3255, -0.0016818, 0.0, 1.4678, 1.8767]
    _viscosity_constants = [-6.894, 818.6, -0.5941]
    _thermal_conductivity_constants = [0.18334, -0.0002228]
    _vapor_pressure_constants = [88.671, 0.0, -10.045, 7.46e-06, 2.0]
    _enthalpy_constants = [4.8287, 0.37804]
