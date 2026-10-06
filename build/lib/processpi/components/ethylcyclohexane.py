from .base import Component
from processpi.units import *

class Ethylcyclohexane(Component):
    """
    Represents the properties and constants for Ethylcyclohexane(C8?H16?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylcyclohexane, which are essential for various process engineering calculations.
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
    name = "Ethylcyclohexane"
    formula = "C8?H16?"
    molecular_weight = 112.213

    # Critical properties
    _critical_temperature = Temperature(609.15, "K")
    _critical_pressure = Pressure(3.04, "MPa")
    _critical_volume = Volume(0.43, "m3")
    _critical_zc = 0.258
    _critical_acentric_factor = 0.2455

    _density_constants = [0.61587, 0.26477, 609.15, 0.28054]
    _specific_heat_constants = [0.0, 72.74, 0.64738, 0.0, 0.0, 1.6109, 2.6798]
    _viscosity_constants = [-22.11, 1673.0, 1.641]
    _thermal_conductivity_constants = [0.17662, -0.0002014]
    _vapor_pressure_constants = [80.208, 0.0, -8.6023, 4.59e-06, 2.0]
    _enthalpy_constants = [5.3832, 0.41763]
