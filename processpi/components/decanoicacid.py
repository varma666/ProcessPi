from .base import Component
from processpi.units import *

class DecanoicAcid(Component):
    """
    Represents the properties and constants for Decanoic acid(C10?H20?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Decanoic acid, which are essential for various process engineering calculations.
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
    name = "Decanoic acid"
    formula = "C10?H20?O2?"
    molecular_weight = 172.265

    # Critical properties
    _critical_temperature = Temperature(722.1, "K")
    _critical_pressure = Pressure(2.28, "MPa")
    _critical_volume = Volume(0.639, "m3")
    _critical_zc = 0.243
    _critical_acentric_factor = 0.8126

    _density_constants = [0.39348, 0.2492, 722.1, 0.28571]
    _specific_heat_constants = [0.0, 140.41, 0.9968, 0.0, 0.0, 3.5521, 5.9017]
    _viscosity_constants = [-12.305, 2324.1, -0.055494]
    _thermal_conductivity_constants = [0.206, -0.0002]
    _vapor_pressure_constants = [123.36, 0.0, -13.474, 1.95e-18, 6.0]
    _enthalpy_constants = [13.107, 1.0674, -0.97372, 0.40491]
