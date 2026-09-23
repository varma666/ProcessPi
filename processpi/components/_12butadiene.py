from .base import Component
from processpi.units import *

class _12Butadiene(Component):
    """
    Represents the properties and constants for 12Butadiene(C4?H6?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 12Butadiene, which are essential for various process engineering calculations.
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
    name = "12Butadiene"
    formula = "C4?H6?"
    molecular_weight = 54.09

    # Critical properties
    _critical_temperature = Temperature(452.0, "K")
    _critical_pressure = Pressure(4.36, "MPa")
    _critical_volume = Volume(0.22, "m3")
    _critical_zc = 0.255
    _critical_acentric_factor = 0.1659

    _density_constants = [1.187, 0.26114, 452.0, 0.3065]
    _specific_heat_constants = [0.0, -311.14, 0.97007, -0.0001523, 0.0, 1.1034, 1.2279]
    _viscosity_constants = [-10.143, 472.79, -0.028241]
    _thermal_conductivity_constants = [0.21966, -0.0003436]
    _vapor_pressure_constants = [39.714, 0.0, -2.6407, 6.94e-18, 6.0]
    _enthalpy_constants = [3.522, 0.395]
