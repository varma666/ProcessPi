from .base import Component
from processpi.units import *

class _1Propanol(Component):
    """
    Represents the properties and constants for 1Propanol(C3H8O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Propanol, which are essential for various process engineering calculations.
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
    name = "1Propanol"
    formula = "C3H8O"
    molecular_weight = 60.095

    # Critical properties
    _critical_temperature = Temperature(536.8, "K")
    _critical_pressure = Pressure(5.169, "MPa")
    _critical_volume = Volume(0.219, "m3")
    _critical_zc = 0.254
    _critical_acentric_factor = 0.6209

    _density_constants = [1.2457, 0.27281, 536.8, 0.23994]
    # Liquid Cp, J/(kmol K), 146.95-400 K: Perry's Chemical Engineers'
    # Handbook, 8th ed., Table 2-153, p. 2-169. C1 is 158,760; the thousands
    # comma had turned it into 0.0, and the table's Cp at Tmin and Tmax
    # (1.0797E5, 2.198E5) had been appended as two more constants.
    _specific_heat_constants = [158760, -635.0, 1.969, 0.0, 0.0]
    _viscosity_constants = [23.467, 116.07, -5.3372, 2880000000.0, -4.0267]
    _thermal_conductivity_constants = [0.2203, -0.0002155]
    # Vapour pressure, Pa: Perry's 8th ed., Table 2-8, p. 2-59. C2 is
    # -8,307.2; the thousands comma had turned it into 0.0.
    _vapor_pressure_constants = [84.6642, -8307.2, -8.5767, 7.51e-18, 6.0]
    # Heat of vaporization, J/kmol, 146.95-536.8 K: Perry's 8th ed., Table
    # 2-150, p. 2-154. The table prints C1 x 1E-07 = 6.8988; C5 is blank (0).
    _enthalpy_constants = [6.8988E7, 0.6458, -0.5384, 0.3317, 0]
