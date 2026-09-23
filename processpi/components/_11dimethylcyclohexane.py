from .base import Component
from processpi.units import *

class _11Dimethylcyclohexane(Component):
    """
    Represents the properties and constants for 11Dimethylcyclohexane(C8?H16?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 11Dimethylcyclohexane, which are essential for various process engineering calculations.
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
    name = "11Dimethylcyclohexane"
    formula = "C8?H16?"
    molecular_weight = 112.213

    # Critical properties
    _critical_temperature = Temperature(591.15, "K")
    _critical_pressure = Pressure(2.938, "MPa")
    _critical_volume = Volume(0.45, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.2326

    _density_constants = [0.55873, 0.25143, 591.15, 0.27758]
    _specific_heat_constants = [0.0, 8.765, 0.81151, 0.0, 0.0, 1.8321, 2.6309]
    _viscosity_constants = [-10.716, 1140.5, -0.047736]
    _thermal_conductivity_constants = [0.1807, -0.0002177]
    _vapor_pressure_constants = [81.184, 0.0, -8.8498, 5.46e-06, 2.0]
    _enthalpy_constants = [5.0402, 0.4036]
