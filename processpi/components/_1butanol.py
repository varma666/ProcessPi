from .base import Component
from processpi.units import *

class _1Butanol(Component):
    """
    Represents the properties and constants for 1Butanol(C4?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Butanol, which are essential for various process engineering calculations.
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
    name = "1Butanol"
    formula = "C4?H10?O"
    molecular_weight = 74.122

    # Critical properties
    _critical_temperature = Temperature(563.1, "K")
    _critical_pressure = Pressure(4.414, "MPa")
    _critical_volume = Volume(0.273, "m3")
    _critical_zc = 0.258
    _critical_acentric_factor = 0.5883

    _density_constants = [0.98279, 0.2683, 563.1, 0.25488]
    _specific_heat_constants = [0.0, -730.4, 2.2998, 0.0, 0.0, 1.3465, 2.5817]
    _viscosity_constants = [0.87669, 1602.9, -2.1475, 3.39e+22, -9.9231]
    _thermal_conductivity_constants = [0.2136, -0.0002034]
    _vapor_pressure_constants = [106.295, 0.0, -11.655, 1.08e-17, 6.0]
    _enthalpy_constants = [7.1274, 0.0483, 0.8966, -0.5116]
