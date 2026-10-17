from .base import Component
from processpi.units import *

class Nitrogen(Component):
    """
    Represents the properties and constants for Nitrogen(N2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nitrogen, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 249, in the equation forms `Component` uses.
    At 25 C and 1 atm nitrogen is a gas: `specific_heat()` and
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
    name = "Nitrogen"
    formula = "N2"
    # Molecular weight and critical properties: Table 2-141, p. 2-141.
    molecular_weight = 28.013
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "inert_gas"
    _hx_velocity_key = "nitrogen"

    # Critical properties
    _critical_temperature = Temperature(126.2, "K")
    _critical_pressure = Pressure(3.4, "MPa")
    _critical_volume = Volume(0.08921, "m3")
    _critical_zc = 0.289
    _critical_acentric_factor = 0.0377

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 63.15-126.2 K: Table 2-32, p. 2-102.
    _density_constants = [3.2091, 0.2861, 126.2, 0.2966]
    # Liquid Cp, polynomial, J/(kmol K), 63.15-112 K: Table 2-153, p. 2-169.
    _specific_heat_constants = [281970, -12281, 248, -2.2182, 0.0074902]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 63.15-124 K: Table 2-313, p. 2-431.
    _viscosity_constants = [16.004, -181.61, -5.1551, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 63.15-124 K:
    # Table 2-315, p. 2-443.
    _thermal_conductivity_constants = [0.2654, -0.001677, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 63.15-126.2 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [58.282, -1084.1, -8.3144, 4.4127E-02, 1]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 63.15-126.2 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 0.74905).
    _enthalpy_constants = [7.4905E6, 0.40406, -0.317, 0.27343, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 50-1500 K: Table 2-156, p. 2-180
    # (C1 = 0.29105E5, C2 = 0.086149E5, C3 = 1.7016E3, C4 = 0.0010347E5, C5 = 909.79).
    _ideal_gas_heat_capacity_constants = [0.29105E5, 0.086149E5, 1.7016E3, 0.0010347E5, 909.79]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 63.15-2000 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [0.00033143, 0.7722, 16.323, 373.72]
