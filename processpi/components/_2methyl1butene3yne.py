from .base import Component
from processpi.units import *

class _2Methyl1Butene3Yne(Component):
    """
    Represents the properties and constants for 2Methyl1butene3yne(C5?H6?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Methyl1butene3yne, which are essential for various process engineering calculations.
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
    name = "2Methyl1butene3yne"
    formula = "C5?H6?"
    molecular_weight = 66.101

    # Critical properties
    _critical_temperature = Temperature(492.0, "K")
    _critical_pressure = Pressure(4.38, "MPa")
    _critical_volume = Volume(0.248, "m3")
    _critical_zc = 0.266
    _critical_acentric_factor = 0.137

    _density_constants = [1.1157, 0.27671, 492.0, 0.30821]
    _specific_heat_constants = [0.0, 181.01, 0.0, 0.0, 0.0, 1.3589, 1.372]
    _viscosity_constants = [-3.6585, 441.1, -1.0547]
    _thermal_conductivity_constants = [0.20385, -0.0002874]
    _vapor_pressure_constants = [95.453, 0.0, -12.384, 0.0156, 1.0]
    _enthalpy_constants = [3.648, 0.3863]
