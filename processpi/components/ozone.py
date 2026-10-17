from .base import Component
from processpi.units import *

class Ozone(Component):
    """
    Represents the properties and constants for Ozone(O3).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ozone, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 276, in the equation forms `Component` uses.
    At 25 C and 1 atm ozone is a gas: `specific_heat()` and
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
    name = "Ozone"
    formula = "O3"
    # Molecular weight and critical properties: Table 2-141, p. 2-141.
    molecular_weight = 47.998
    # Heat exchanger data, read by Component.hx_data() and httype()
    # An oxidiser, not an inert gas: CORROSION_SEVERITY_DATABASE has no
    # oxidiser row, so it takes the generic low-medium "hydrocarbon" row.
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "ozone"

    # Critical properties
    _critical_temperature = Temperature(261, "K")
    _critical_pressure = Pressure(5.57, "MPa")
    _critical_volume = Volume(0.089, "m3")
    _critical_zc = 0.228
    _critical_acentric_factor = 0.2119

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 80.15-261 K: Table 2-32, p. 2-102.
    _density_constants = [3.3592, 0.29884, 261, 0.28523]
    # Liquid Cp, polynomial, J/(kmol K), 90-150 K: Table 2-153, p. 2-169.
    _specific_heat_constants = [60046, 281.16, 0, 0, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 77.55-208.8 K: Table 2-313, p. 2-431.
    _viscosity_constants = [-10.94, 415.96, 0, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 77.35-161.85 K:
    # Table 2-315, p. 2-443.
    _thermal_conductivity_constants = [0.17483, 0.00075288, -2.5228E-06, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 80.15-261 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [40.067, -2204.8, -2.9351, 7.7520E-16, 6]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 80.15-261 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 1.8587).
    _enthalpy_constants = [1.8587E7, 0.30416, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K: Table 2-156, p. 2-180
    # (C1 = 0.33483E5, C2 = 0.29577E5, C3 = 1.5217E3, C4 = 0.27151E5, C5 = 680.35).
    _ideal_gas_heat_capacity_constants = [0.33483E5, 0.29577E5, 1.5217E3, 0.27151E5, 680.35]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 161.85-1000 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [0.0043147, 0.47999, 700.09, 0]
