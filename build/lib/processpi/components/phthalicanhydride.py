from .base import Component
from processpi.units import *

class PhthalicAnhydride(Component):
    """
    Represents the properties and constants for Phthalic anhydride(C8?H4?O3?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Phthalic anhydride, which are essential for various process engineering calculations.
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
    name = "Phthalic anhydride"
    formula = "C8?H4?O3?"
    molecular_weight = 148.116

    # Critical properties
    _critical_temperature = Temperature(791.0, "K")
    _critical_pressure = Pressure(4.72, "MPa")
    _critical_volume = Volume(0.421, "m3")
    _critical_zc = 0.302
    _critical_acentric_factor = 0.7025

    _density_constants = [0.5393, 0.22704, 791.0, 0.248]
    _specific_heat_constants = [0.0, 252.4, 0.0, 0.0, 0.0, 2.4741, 2.8615]
    _viscosity_constants = [195.25, -11072.0, -29.084]
    _thermal_conductivity_constants = [0.22946, -0.00021345]
    _vapor_pressure_constants = [126.5, 0.0, -15.002, 7.75e-06, 2.0]
    _enthalpy_constants = [6.916, 0.1755]
