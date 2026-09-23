from .base import Component
from processpi.units import *

class _13Butadiene(Component):
    """
    Represents the properties and constants for 13Butadiene(C4?H6?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 13Butadiene, which are essential for various process engineering calculations.
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
    name = "13Butadiene"
    formula = "C4?H6?"
    molecular_weight = 54.09

    # Critical properties
    _critical_temperature = Temperature(425.0, "K")
    _critical_pressure = Pressure(4.32, "MPa")
    _critical_volume = Volume(0.221, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.195

    _density_constants = [1.2346, 0.27216, 425.0, 0.28707]
    _specific_heat_constants = [0.0, -323.1, 1.015, 3.2e-05, 0.0, 1.0333, 1.4148]
    _viscosity_constants = [17.844, -310.2, -4.5058]
    _thermal_conductivity_constants = [0.22231, -0.0003664]
    _vapor_pressure_constants = [75.572, 0.0, -8.5323, 1.23e-05, 2.0]
    _enthalpy_constants = [3.2632, 0.3701]
