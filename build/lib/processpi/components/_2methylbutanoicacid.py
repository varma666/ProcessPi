from .base import Component
from processpi.units import *

class _2MethylbutanoicAcid(Component):
    """
    Represents the properties and constants for 2Methylbutanoic acid(C5?H10?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Methylbutanoic acid, which are essential for various process engineering calculations.
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
    name = "2Methylbutanoic acid"
    formula = "C5?H10?O2?"
    molecular_weight = 102.132

    # Critical properties
    _critical_temperature = Temperature(643.0, "K")
    _critical_pressure = Pressure(3.89, "MPa")
    _critical_volume = Volume(0.347, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.5894

    _density_constants = [0.72762, 0.25244, 643.0, 0.28571]
    _specific_heat_constants = [0.0, 417.4, 0.0, 0.0, 0.0, 2.0839, 2.7518]
    _viscosity_constants = [-1.035, 1048.5, -1.5474]
    _thermal_conductivity_constants = [0.22284, -0.0002516]
    _vapor_pressure_constants = [85.383, 0.0, -8.6164, 5.61e-18, 6.0]
    _enthalpy_constants = [7.48, 0.3933]
