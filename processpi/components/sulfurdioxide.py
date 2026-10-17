from .base import Component
from processpi.units import *

class SulfurDioxide(Component):
    """
    Represents the properties and constants for Sulfur Dioxide(SO2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Sulfur Dioxide, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 314, in the equation forms `Component` uses.
    At 25 C and 1 atm sulfur dioxide is a gas: `specific_heat()` and
    `thermal_conductivity()` then use the ideal-gas Cp and the vapour k below,
    and `viscosity()` the base class's Sutherland fallback (air constants).

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
    - `_ideal_gas_heat_capacity_constants`: Ideal-gas Cp, used in the gas phase.
    - `_vapor_thermal_conductivity_constants`: Vapour thermal conductivity, used
      in the gas phase.
    """
    name = "Sulfur Dioxide"
    formula = "SO2"
    # Molecular weight and critical properties: Table 2-141, p. 2-142.
    molecular_weight = 64.064
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "acid"
    _hx_velocity_key = "sulfur_dioxide"

    # Critical properties
    _critical_temperature = Temperature(430.75, "K")
    _critical_pressure = Pressure(7.884, "MPa")
    _critical_volume = Volume(0.122, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.2454

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 197.67-430.75 K: Table 2-32, p. 2-103.
    _density_constants = [2.106, 0.25842, 430.75, 0.2895]
    # Liquid Cp, polynomial, J/(kmol K), 197.67-350 K: Table 2-153, p. 2-170.
    _specific_heat_constants = [85743, 5.7443, 0, 0, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 225-400 K: Table 2-313, p. 2-432.
    _viscosity_constants = [46.223, -1378, -8.7475, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 197.67-400 K:
    # Table 2-315, p. 2-444.
    _thermal_conductivity_constants = [0.38218, -0.0006254, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 197.67-430.75 K: Table 2-8, p. 2-60.
    _vapor_pressure_constants = [47.365, -4084.5, -3.6469, 1.7990E-17, 6]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 197.67-430.75 K:
    # Table 2-150, p. 2-155 (C1 x 1E-07 = 3.676).
    _enthalpy_constants = [3.676E7, 0.4, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K: Table 2-156, p. 2-181
    # (C1 = 0.33375E5, C2 = 0.25864E5, C3 = 0.9328E3, C4 = 0.1088E5, C5 = 423.7).
    _ideal_gas_heat_capacity_constants = [0.33375E5, 0.25864E5, 0.9328E3, 0.1088E5, 423.7]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 250-900 K:
    # Table 2-314, p. 2-438.
    _vapor_thermal_conductivity_constants = [10.527, -0.7732, -1333, 1506400]
