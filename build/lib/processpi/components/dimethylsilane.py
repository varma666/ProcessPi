from .base import Component
from processpi.units import *

class Dimethylsilane(Component):
    """
    Represents the properties and constants for Dimethylsilane(C2?H8?Si).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dimethylsilane, which are essential for various process engineering calculations.
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
    name = "Dimethylsilane"
    formula = "C2?H8?Si"
    molecular_weight = 60.17

    # Critical properties
    _critical_temperature = Temperature(402.0, "K")
    _critical_pressure = Pressure(3.56, "MPa")
    _critical_volume = Volume(0.258, "m3")
    _critical_zc = 0.275
    _critical_acentric_factor = 0.13

    _density_constants = [1.0214, 0.26351, 402.0, 0.28421]
    _specific_heat_constants = [0.0, 0.0, 0.0, 0.0, 0.0, 1.3181, 1.3181]
    _viscosity_constants = []
    _thermal_conductivity_constants = [0.25547, -0.0004411]
    _vapor_pressure_constants = [63.08, 0.0, -6.425, 1.51e-16, 6.0]
    _enthalpy_constants = [2.8365, 0.35393]
