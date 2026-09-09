from .base import Component
from processpi.units import *

class Acetaldehyde(Component):
    """
    Represents the properties and constants for Acetaldehyde(C2?H4?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acetaldehyde, which are essential for various process engineering calculations.
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
    name = "Acetaldehyde"
    formula = "C2H4O"
    molecular_weight = 44.053

    # Critical properties
    _critical_temperature = Temperature(466.0, "K")
    _critical_pressure = Pressure(5.55, "MPa")
    _critical_volume = Volume(0.154, "m3")
    _critical_zc = 0.221
    _critical_acentric_factor = 0.2907

    _density_constants = [1.6994, 0.26167, 466.0, 0.2913]
    _specific_heat_constants = [0.0, -433.0, 1.425, 0.0, 0.0, 0.8221, 1.1097]
    _viscosity_constants = [-5.895, 668.21, -0.84323]
    _thermal_conductivity_constants = [0.311, -0.000436]
    _vapor_pressure_constants = [193.69, 0.0, -29.502, 0.0437, 1.0]
    _enthalpy_constants = [3.8366, 0.40081]
