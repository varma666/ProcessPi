from .base import Component
from processpi.units import *

class _1Octene(Component):
    """
    Represents the properties and constants for 1Octene(C8?H16?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Octene, which are essential for various process engineering calculations.
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
    name = "1Octene"
    formula = "C8?H16?"
    molecular_weight = 112.213

    # Critical properties
    _critical_temperature = Temperature(566.9, "K")
    _critical_pressure = Pressure(2.663, "MPa")
    _critical_volume = Volume(0.464, "m3")
    _critical_zc = 0.262
    _critical_acentric_factor = 0.3921

    _density_constants = [0.55449, 0.25952, 566.9, 0.28571]
    _specific_heat_constants = [0.0, 0.0, 21.477, -0.044462, 3.5e-05, 2.1327, 2.8235]
    _viscosity_constants = [-11.19, 1057.4]
    _thermal_conductivity_constants = [0.20467, -0.0002675]
    _vapor_pressure_constants = [74.936, 0.0, -7.5843, 1.71e-17, 6.0]
    _enthalpy_constants = [5.4859, 0.26207, 0.50642, -0.43873]
