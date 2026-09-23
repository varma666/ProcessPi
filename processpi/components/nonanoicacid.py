from .base import Component
from processpi.units import *

class NonanoicAcid(Component):
    """
    Represents the properties and constants for Nonanoic acid(C9?H18?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nonanoic acid, which are essential for various process engineering calculations.
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
    name = "Nonanoic acid"
    formula = "C9?H18?O2?"
    molecular_weight = 158.238

    # Critical properties
    _critical_temperature = Temperature(710.7, "K")
    _critical_pressure = Pressure(2.514, "MPa")
    _critical_volume = Volume(0.584, "m3")
    _critical_zc = 0.248
    _critical_acentric_factor = 0.7724

    _density_constants = [0.41582, 0.24284, 710.7, 0.30036]
    _specific_heat_constants = [0.0, 49.726, 0.9813, 0.0, 0.0, 3.1855, 5.2498]
    _viscosity_constants = [-48.851, 4095.0, 5.294]
    _thermal_conductivity_constants = [0.204, -0.0002]
    _vapor_pressure_constants = [137.6, 0.0, -15.618, 5.57e-18, 6.0]
    _enthalpy_constants = [12.38, 0.69869, 0.097854, -0.35082]
