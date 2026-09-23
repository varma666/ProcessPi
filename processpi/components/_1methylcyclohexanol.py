from .base import Component
from processpi.units import *

class _1Methylcyclohexanol(Component):
    """
    Represents the properties and constants for 1Methylcyclohexanol(C7?H14?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Methylcyclohexanol, which are essential for various process engineering calculations.
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
    name = "1Methylcyclohexanol"
    formula = "C7?H14?O"
    molecular_weight = 114.185

    # Critical properties
    _critical_temperature = Temperature(686.0, "K")
    _critical_pressure = Pressure(4.0, "MPa")
    _critical_volume = Volume(0.374, "m3")
    _critical_zc = 0.262
    _critical_acentric_factor = 0.2213

    _density_constants = [0.7013, 0.266, 686.0, 0.28571]
    _specific_heat_constants = [0.0, 508.59, 0.0, 0.0, 0.0, 2.0315, 2.7494]
    _viscosity_constants = [-6.1534, 3219.0, -1.4494]
    _thermal_conductivity_constants = [0.21558, -0.00022728]
    _vapor_pressure_constants = [134.63, 0.0, -16.511, 8.44e-06, 2.0]
    _enthalpy_constants = [6.477, 0.4853]
