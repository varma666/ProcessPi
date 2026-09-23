from .base import Component
from processpi.units import *

class _2MethyloctanoicAcid(Component):
    """
    Represents the properties and constants for 2Methyloctanoic acid(C9?H18?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Methyloctanoic acid, which are essential for various process engineering calculations.
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
    name = "2Methyloctanoic acid"
    formula = "C9?H18?O2?"
    molecular_weight = 158.238

    # Critical properties
    _critical_temperature = Temperature(694.0, "K")
    _critical_pressure = Pressure(2.54, "MPa")
    _critical_volume = Volume(0.572, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.7913

    _density_constants = [0.4416, 0.2521, 694.0, 0.28532]
    _specific_heat_constants = [0.0, 15.421, 1.0578, 0.0, 0.0, 2.9128, 5.1864]
    _viscosity_constants = [-12.579, 2224.2]
    _thermal_conductivity_constants = [0.20911, -0.00021852]
    _vapor_pressure_constants = [105.7, 0.0, -11.234, 4.46e-18, 6.0]
    _enthalpy_constants = [10.53, 0.7454, -0.39297, 0.047214]
