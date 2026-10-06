from .base import Component
from processpi.units import *

class Trans12Dimethylcyclohexane(Component):
    """
    Represents the properties and constants for trans12Dimethylcyclohexane(C8?H16?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for trans12Dimethylcyclohexane, which are essential for various process engineering calculations.
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
    name = "trans12Dimethylcyclohexane"
    formula = "C8?H16?"
    molecular_weight = 112.213

    # Critical properties
    _critical_temperature = Temperature(596.15, "K")
    _critical_pressure = Pressure(2.938, "MPa")
    _critical_volume = Volume(0.46, "m3")
    _critical_zc = 0.273
    _critical_acentric_factor = 0.2379

    _density_constants = [0.54405, 0.25026, 596.15, 0.2658]
    _specific_heat_constants = [0.0, -145.26, 1.0932, 0.0, 0.0, 1.661, 2.6989]
    _viscosity_constants = [-11.344, 1168.9, 0.04513]
    _thermal_conductivity_constants = [0.17675, -0.0002077]
    _vapor_pressure_constants = [78.429, 0.0, -8.4129, 4.98e-06, 2.0]
    _enthalpy_constants = [5.1194, 0.405]
