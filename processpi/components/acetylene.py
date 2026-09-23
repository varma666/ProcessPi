from .base import Component
from processpi.units import *

class Acetylene(Component):
    """
    Represents the properties and constants for Acetylene(C2?H2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acetylene, which are essential for various process engineering calculations.
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
    name = "Acetylene"
    formula = "C2?H2?"
    molecular_weight = 26.037

    # Critical properties
    _critical_temperature = Temperature(308.3, "K")
    _critical_pressure = Pressure(6.138, "MPa")
    _critical_volume = Volume(0.112, "m3")
    _critical_zc = 0.268
    _critical_acentric_factor = 0.1912

    _density_constants = [2.4507, 0.27448, 308.3, 0.28752]
    _specific_heat_constants = [0.0, 0.0, -15.895, 0.027732, 0.0, 0.8021, 0.8853]
    _viscosity_constants = [6.224, -151.8, -2.6554]
    _thermal_conductivity_constants = [0.33363, -0.00083655]
    _vapor_pressure_constants = [39.63, 0.0, -2.78, 2.39e-16, 6.0]
    _enthalpy_constants = [2.3214, 0.35938]
