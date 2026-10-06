from .base import Component
from processpi.units import *

class Dichloromethane(Component):
    """
    Represents the properties and constants for Dichloromethane(CH2?Cl2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dichloromethane, which are essential for various process engineering calculations.
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
    name = "Dichloromethane"
    formula = "CH2?Cl2?"
    molecular_weight = 84.933

    # Critical properties
    _critical_temperature = Temperature(510.0, "K")
    _critical_pressure = Pressure(6.08, "MPa")
    _critical_volume = Volume(0.185, "m3")
    _critical_zc = 0.265
    _critical_acentric_factor = 0.1986

    _density_constants = [1.3897, 0.25678, 510.0, 0.2902]
    _specific_heat_constants = [0.0, -62.941, 0.23265, 0.0, 0.0, 0.9518, 1.0265]
    _viscosity_constants = [-13.071, 940.03, 0.3733]
    _thermal_conductivity_constants = [0.23847, -0.00033366]
    _vapor_pressure_constants = [101.6, 0.0, -12.247, 1.23e-05, 2.0]
    _enthalpy_constants = [4.186, 0.4092]
