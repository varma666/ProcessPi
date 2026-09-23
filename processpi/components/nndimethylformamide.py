from .base import Component
from processpi.units import *

class NndimethylFormamide(Component):
    """
    Represents the properties and constants for NNDimethyl formamide(C3?H7?NO).

    This class provides a comprehensive set of physical and thermodynamic properties
    for NNDimethyl formamide, which are essential for various process engineering calculations.
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
    name = "NNDimethyl formamide"
    formula = "C3?H7?NO"
    molecular_weight = 73.094

    # Critical properties
    _critical_temperature = Temperature(649.6, "K")
    _critical_pressure = Pressure(4.42, "MPa")
    _critical_volume = Volume(0.26199, "m3")
    _critical_zc = 0.214
    _critical_acentric_factor = 0.3177

    _density_constants = [0.89615, 0.23478, 649.6, 0.28091]
    _specific_heat_constants = [0.0, -106.0, 0.384, 0.0, 0.0, 1.4767, 1.82]
    _viscosity_constants = [-20.425, 1515.5, 1.4444]
    _thermal_conductivity_constants = [0.26, -0.000255]
    _vapor_pressure_constants = [82.762, 0.0, -8.8038, 4.24e-06, 2.0]
    _enthalpy_constants = [5.9217, 0.37996]
