from .base import Component
from processpi.units import *

class Propionaldehyde(Component):
    """
    Represents the properties and constants for Propionaldehyde(C3?H6?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Propionaldehyde, which are essential for various process engineering calculations.
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
    name = "Propionaldehyde"
    formula = "C3?H6?O"
    molecular_weight = 58.079

    # Critical properties
    _critical_temperature = Temperature(504.4, "K")
    _critical_pressure = Pressure(4.92, "MPa")
    _critical_volume = Volume(0.204, "m3")
    _critical_zc = 0.239
    _critical_acentric_factor = 0.2559

    _density_constants = [1.296, 0.26439, 504.4, 0.29471]
    _specific_heat_constants = [0.0, 115.73, 0.0, 0.0, 0.0, 1.2245, 1.3735]
    _viscosity_constants = [-9.9177, 839.53, -0.16735]
    _thermal_conductivity_constants = [0.2498, -0.00030075]
    _vapor_pressure_constants = [80.581, 0.0, -8.9301, 8.22e-06, 2.0]
    _enthalpy_constants = [4.1492, 0.36751]
