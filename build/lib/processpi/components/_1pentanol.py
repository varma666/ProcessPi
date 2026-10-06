from .base import Component
from processpi.units import *

class _1Pentanol(Component):
    """
    Represents the properties and constants for 1Pentanol(C5?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Pentanol, which are essential for various process engineering calculations.
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
    name = "1Pentanol"
    formula = "C5?H12?O"
    molecular_weight = 88.148

    # Critical properties
    _critical_temperature = Temperature(588.1, "K")
    _critical_pressure = Pressure(3.897, "MPa")
    _critical_volume = Volume(0.326, "m3")
    _critical_zc = 0.258
    _critical_acentric_factor = 0.5748

    _density_constants = [0.81754, 0.26732, 588.1, 0.25348]
    _specific_heat_constants = [0.0, -651.3, 2.275, 0.0, 0.0, 1.6198, 2.9227]
    _viscosity_constants = [-36.561, 3542.2, 3.3364, -8.05e-37, 12.84]
    _thermal_conductivity_constants = [0.2006, -0.0001603]
    _vapor_pressure_constants = [114.748, 0.0, -12.858, 1.25e-17, 6.0]
    _enthalpy_constants = [7.39, -0.1464, 1.4751, -0.9208]
