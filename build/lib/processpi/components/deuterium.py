from .base import Component
from processpi.units import *

class Deuterium(Component):
    """
    Represents the properties and constants for Deuterium(D2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Deuterium, which are essential for various process engineering calculations.
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
    name = "Deuterium"
    formula = "D2?"
    molecular_weight = 4.032

    # Critical properties
    _critical_temperature = Temperature(38.35, "K")
    _critical_pressure = Pressure(1.6617, "MPa")
    _critical_volume = Volume(0.060263, "m3")
    _critical_zc = 0.314
    _critical_acentric_factor = -0.1449

    _density_constants = [5.2115, 0.315, 38.35, 0.28571]
    _specific_heat_constants = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    _viscosity_constants = [1.348e-06]
    _thermal_conductivity_constants = [1.264]
    _vapor_pressure_constants = [18.947, -154.47, -0.5723, 0.0389, 1.0]
    _enthalpy_constants = [0.1657, 0.352]
