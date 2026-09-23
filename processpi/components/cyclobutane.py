from .base import Component
from processpi.units import *

class Cyclobutane(Component):
    """
    Represents the properties and constants for Cyclobutane(C4?H8?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Cyclobutane, which are essential for various process engineering calculations.
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
    name = "Cyclobutane"
    formula = "C4?H8?"
    molecular_weight = 56.106

    # Critical properties
    _critical_temperature = Temperature(459.93, "K")
    _critical_pressure = Pressure(4.98, "MPa")
    _critical_volume = Volume(0.21, "m3")
    _critical_zc = 0.273
    _critical_acentric_factor = 0.1847

    _density_constants = [1.3931, 0.29255, 459.93, 0.24913]
    _specific_heat_constants = [0.0, -215.81, 0.8103, 0.0, 0.0, 0.9017, 1.0961]
    _viscosity_constants = [-3.4968, 397.94, -1.1087]
    _thermal_conductivity_constants = [0.22262, -0.00034082]
    _vapor_pressure_constants = [85.899, 0.0, -10.883, 0.0149, 1.0]
    _enthalpy_constants = [3.334, 0.3395]
