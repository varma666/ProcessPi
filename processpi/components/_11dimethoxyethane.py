from .base import Component
from processpi.units import *

class _11Dimethoxyethane(Component):
    """
    Represents the properties and constants for 11Dimethoxyethane(C4?H10?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 11Dimethoxyethane, which are essential for various process engineering calculations.
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
    name = "11Dimethoxyethane"
    formula = "C4?H10?O2?"
    molecular_weight = 90.121

    # Critical properties
    _critical_temperature = Temperature(507.8, "K")
    _critical_pressure = Pressure(3.773, "MPa")
    _critical_volume = Volume(0.297, "m3")
    _critical_zc = 0.265
    _critical_acentric_factor = 0.3277

    _density_constants = [0.89368, 0.26599, 507.8, 0.28571]
    _specific_heat_constants = [0.0, -313.41, 1.1023, 0.0, 0.0, 1.6586, 2.0755]
    _viscosity_constants = [-10.968, 885.49]
    _thermal_conductivity_constants = [0.22078, -0.00031271]
    _vapor_pressure_constants = [53.637, 0.0, -4.5649, 1.68e-17, 6.0]
    _enthalpy_constants = [4.3872, 0.56226, -0.60662, 0.4202]
