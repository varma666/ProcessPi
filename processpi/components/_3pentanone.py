from .base import Component
from processpi.units import *

class _3Pentanone(Component):
    """
    Represents the properties and constants for 3Pentanone(C5?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 3Pentanone, which are essential for various process engineering calculations.
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
    name = "3Pentanone"
    formula = "C5?H10?O"
    molecular_weight = 86.132

    # Critical properties
    _critical_temperature = Temperature(560.95, "K")
    _critical_pressure = Pressure(3.74, "MPa")
    _critical_volume = Volume(0.336, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.3448

    _density_constants = [0.71811, 0.24129, 560.95, 0.27996]
    _specific_heat_constants = [0.0, -176.43, 0.5669, 0.0, 0.0, 1.8279, 2.0661]
    _viscosity_constants = [-2.8695, 596.32, -1.2025]
    _thermal_conductivity_constants = [0.21569, -0.00024081]
    _vapor_pressure_constants = [44.286, 0.0, -3.0913, 1.86e-18, 6.0]
    _enthalpy_constants = [5.2359, 0.40465]
