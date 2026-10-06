from .base import Component
from processpi.units import *

class _3Heptanone(Component):
    """
    Represents the properties and constants for 3Heptanone(C7?H14?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 3Heptanone, which are essential for various process engineering calculations.
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
    name = "3Heptanone"
    formula = "C7?H14?O"
    molecular_weight = 114.185

    # Critical properties
    _critical_temperature = Temperature(606.6, "K")
    _critical_pressure = Pressure(2.92, "MPa")
    _critical_volume = Volume(0.433, "m3")
    _critical_zc = 0.251
    _critical_acentric_factor = 0.4076

    _density_constants = [0.59268, 0.25663, 606.6, 0.27766]
    _specific_heat_constants = [0.0, -399.89, 1.0601, 0.0, 0.0, 2.3522, 3.2303]
    _viscosity_constants = [-9.3874, 1204.9, -0.32618]
    _thermal_conductivity_constants = [0.2026, -0.0002234]
    _vapor_pressure_constants = [78.463, 0.0, -7.9062, 8.05e-18, 6.0]
    _enthalpy_constants = [6.3357, 0.42167]
