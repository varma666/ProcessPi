from .base import Component
from processpi.units import *

class Oterphenyl(Component):
    """
    Represents the properties and constants for oTerphenyl(C18?H14?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for oTerphenyl, which are essential for various process engineering calculations.
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
    name = "oTerphenyl"
    formula = "C18?H14?"
    molecular_weight = 230.304

    # Critical properties
    _critical_temperature = Temperature(857.0, "K")
    _critical_pressure = Pressure(2.99, "MPa")
    _critical_volume = Volume(0.731, "m3")
    _critical_zc = 0.307
    _critical_acentric_factor = 0.5513

    _density_constants = [0.3448, 0.25116, 857.0, 0.29268]
    _specific_heat_constants = [0.0, 635.09, 0.0, 0.0, 0.0, 3.9207, 5.6977]
    _viscosity_constants = [-215.09, 11612.0, 31.849, -0.026882, 1.0]
    _thermal_conductivity_constants = [0.16853, -0.00010817]
    _vapor_pressure_constants = [110.52, 0.0, -11.861, 2.21e-18, 6.0]
    _enthalpy_constants = [8.7165, 0.3224]
