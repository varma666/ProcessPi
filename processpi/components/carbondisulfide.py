from .base import Component
from processpi.units import *

class CarbonDisulfide(Component):
    """
    Represents the properties and constants for Carbon disulfide(CS2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Carbon disulfide, which are essential for various process engineering calculations.
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
    name = "Carbon disulfide"
    formula = "CS2?"
    molecular_weight = 76.141

    # Critical properties
    _critical_temperature = Temperature(552.0, "K")
    _critical_pressure = Pressure(7.9, "MPa")
    _critical_volume = Volume(0.16, "m3")
    _critical_zc = 0.275
    _critical_acentric_factor = 0.1107

    _density_constants = [1.7968, 0.28749, 552.0, 0.3226]
    _specific_heat_constants = [0.0, -122.0, 0.5605, -0.001452, 2.01e-06, 0.7577, 1.3125]
    _viscosity_constants = [-10.306, 703.01]
    _thermal_conductivity_constants = [0.2333, -0.000275]
    _vapor_pressure_constants = [67.114, 0.0, -7.5303, 0.00917, 1.0]
    _enthalpy_constants = [3.496, 0.2986]
