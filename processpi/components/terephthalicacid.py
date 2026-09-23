from .base import Component
from processpi.units import *

class TerephthalicAcid(Component):
    """
    Represents the properties and constants for Terephthalic acid(C8?H6?O4?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Terephthalic acid, which are essential for various process engineering calculations.
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
    name = "Terephthalic acid"
    formula = "C8?H6?O4?"
    molecular_weight = 166.131

    # Critical properties
    _critical_temperature = Temperature(1113.0, "K")
    _critical_pressure = Pressure(3.95, "MPa")
    _critical_volume = Volume(0.424, "m3")
    _critical_zc = 0.181
    _critical_acentric_factor = 1.0591

    _density_constants = [0.42685, 0.181, 1113.0, 0.28571]
    _specific_heat_constants = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    _viscosity_constants = []
    _thermal_conductivity_constants = []
    _vapor_pressure_constants = [248.72, 0.0, -30.009, 4.8e-06, 2.0]
    _enthalpy_constants = [8.824, 298.15, 8.824]
