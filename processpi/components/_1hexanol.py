from .base import Component
from processpi.units import *

class _1Hexanol(Component):
    """
    Represents the properties and constants for 1Hexanol(C6?H14?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Hexanol, which are essential for various process engineering calculations.
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
    name = "1Hexanol"
    formula = "C6?H14?O"
    molecular_weight = 102.175

    # Critical properties
    _critical_temperature = Temperature(611.3, "K")
    _critical_pressure = Pressure(3.446, "MPa")
    _critical_volume = Volume(0.382, "m3")
    _critical_zc = 0.259
    _critical_acentric_factor = 0.5586

    _density_constants = [0.70093, 0.26776, 611.3, 0.24919]
    _specific_heat_constants = [0.0, 0.0, 71.721, -0.12026, 7.1087e-05, 1.9821, 3.5197]
    _viscosity_constants = [-39.324, 3841.0, 3.6933, -2.12e-30, 10.485]
    _thermal_conductivity_constants = [0.2193, -0.00022]
    _vapor_pressure_constants = [135.421, 0.0, -15.732, 1.27e-17, 6.0]
    _enthalpy_constants = [7.035, -0.9575, 3.1431, -1.8066]
