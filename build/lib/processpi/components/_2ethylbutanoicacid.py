from .base import Component
from processpi.units import *

class _2EthylButanoicAcid(Component):
    """
    Represents the properties and constants for 2Ethyl butanoic acid(C6?H12?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Ethyl butanoic acid, which are essential for various process engineering calculations.
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
    name = "2Ethyl butanoic acid"
    formula = "C6?H12?O2?"
    molecular_weight = 116.158

    # Critical properties
    _critical_temperature = Temperature(655.0, "K")
    _critical_pressure = Pressure(3.41, "MPa")
    _critical_volume = Volume(0.389, "m3")
    _critical_zc = 0.244
    _critical_acentric_factor = 0.6326

    _density_constants = [0.66085, 0.25707, 655.0, 0.31103]
    _specific_heat_constants = [0.0, 603.02, 0.0, 0.0, 0.0, 2.1203, 3.3794]
    _viscosity_constants = [-12.24, 1836.4, 0.021868]
    _thermal_conductivity_constants = [0.2175, -0.0002407]
    _vapor_pressure_constants = [90.464, 0.0, -9.2836, 5.26e-18, 6.0]
    _enthalpy_constants = [7.898, 0.39445]
