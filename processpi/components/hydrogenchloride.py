from .base import Component
from processpi.units import *

class HydrogenChloride(Component):
    """
    Represents the properties and constants for Hydrogen Chloride(HCl).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hydrogen Chloride, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 185, in the equation forms `Component` uses.
    At 25 C and 1 atm hydrogen chloride is a gas: `specific_heat()` and
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
    name = "Hydrogen Chloride"
    formula = "HCl"
    # Molecular weight and critical properties: Table 2-141, p. 2-140.
    molecular_weight = 36.461
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "acid"
    _hx_velocity_key = "hydrogen_chloride"

    # Critical properties
    _critical_temperature = Temperature(324.65, "K")
    _critical_pressure = Pressure(8.31, "MPa")
    _critical_volume = Volume(0.081, "m3")
    _critical_zc = 0.249
    _critical_acentric_factor = 0.1315

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 158.97-324.65 K: Table 2-32, p. 2-101.
    _density_constants = [3.342, 0.2729, 324.65, 0.3217]
    # Liquid Cp, polynomial, J/(kmol K), 165-185 K: Table 2-153, p. 2-168.
    _specific_heat_constants = [47300, 90, 0, 0, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 158.97-318.15 K: Table 2-313, p. 2-430.
    _viscosity_constants = [-116.34, 3834.6, 16.864, -2.5875E-10, 4]
    # Liquid thermal conductivity, polynomial, W/(m K), 273.15-323.15 K:
    # Table 2-315, p. 2-442.
    _thermal_conductivity_constants = [0.8045, -0.002102, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 158.97-324.65 K: Table 2-8, p. 2-58.
    _vapor_pressure_constants = [104.27, -3731.2, -15.047, 3.1340E-02, 1]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 158.97-324.65 K:
    # Table 2-150, p. 2-153 (C1 x 1E-07 = 2.2093).
    _enthalpy_constants = [2.2093E7, 0.3466, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 50-1500 K: Table 2-156, p. 2-179
    # (C1 = 0.29157E5, C2 = 0.09048E5, C3 = 2.0938E3, C4 = -0.00107E5, C5 = 120).
    _ideal_gas_heat_capacity_constants = [0.29157E5, 0.09048E5, 2.0938E3, -0.00107E5, 120]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 190-700 K:
    # Table 2-314, p. 2-436.
    _vapor_thermal_conductivity_constants = [0.001865, 0.49755, 358, 0]
