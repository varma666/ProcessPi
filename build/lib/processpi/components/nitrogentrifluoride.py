from .base import Component
from processpi.units import *

class NitrogenTrifluoride(Component):
    """
    Represents the properties and constants for Nitrogen trifluoride(F3?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nitrogen trifluoride, which are essential for various process engineering calculations.
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
    name = "Nitrogen trifluoride"
    formula = "F3?N"
    molecular_weight = 71.002

    # Critical properties
    _critical_temperature = Temperature(234.0, "K")
    _critical_pressure = Pressure(4.461, "MPa")
    _critical_volume = Volume(0.11875, "m3")
    _critical_zc = 0.272
    _critical_acentric_factor = 0.12

    _density_constants = [2.3736, 0.2817, 234.0, 0.29529]
    _specific_heat_constants = [0.0, -682.11, 3.8912, 0.0, 0.0, 0.7486, 1.0154]
    _viscosity_constants = []
    _thermal_conductivity_constants = []
    _vapor_pressure_constants = [68.149, 0.0, -8.9118, 0.0232, 1.0]
    _enthalpy_constants = [1.6402, 0.36494]
