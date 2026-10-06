from .base import Component
from processpi.units import *

class _3Octanone(Component):
    """
    Represents the properties and constants for 3Octanone(C8?H16?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 3Octanone, which are essential for various process engineering calculations.
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
    name = "3Octanone"
    formula = "C8?H16?O"
    molecular_weight = 128.212

    # Critical properties
    _critical_temperature = Temperature(627.7, "K")
    _critical_pressure = Pressure(2.704, "MPa")
    _critical_volume = Volume(0.497, "m3")
    _critical_zc = 0.257
    _critical_acentric_factor = 0.4406

    _density_constants = [0.5108, 0.25386, 627.7, 0.26735]
    _specific_heat_constants = [0.0, -417.27, 1.2218, 0.0, 0.0, 2.6314, 3.4335]
    _viscosity_constants = [-20.804, 1834.6, 1.3403]
    _thermal_conductivity_constants = [0.21732, -0.00024969]
    _vapor_pressure_constants = [72.382, 0.0, -7.0002, 5.83e-18, 6.0]
    _enthalpy_constants = [6.6142, 0.58562, -0.40512, 0.22144]
