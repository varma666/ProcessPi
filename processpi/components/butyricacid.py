from .base import Component
from processpi.units import *

class ButyricAcid(Component):
    """
    Represents the properties and constants for Butyric acid(C4?H8?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Butyric acid, which are essential for various process engineering calculations.
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
    name = "Butyric acid"
    formula = "C4?H8?O2?"
    molecular_weight = 88.105

    # Critical properties
    _critical_temperature = Temperature(615.7, "K")
    _critical_pressure = Pressure(4.06, "MPa")
    _critical_volume = Volume(0.293, "m3")
    _critical_zc = 0.232
    _critical_acentric_factor = 0.6805

    _density_constants = [0.88443, 0.25828, 615.7, 0.248]
    _specific_heat_constants = [0.0, -746.4, 1.829, 0.0, 0.0, 1.6902, 2.6031]
    _viscosity_constants = [-9.817, 1388.0, -0.238]
    _thermal_conductivity_constants = [0.1967, -0.000168]
    _vapor_pressure_constants = [93.815, 0.0, -9.8019, 9.31e-18, 6.0]
    _enthalpy_constants = [6.1947, 1.6524, -2.8505, 1.6285]
