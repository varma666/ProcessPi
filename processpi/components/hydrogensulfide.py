from .base import Component, PropertyMethod
from processpi.units import *

class HydrogenSulfide(Component):
    """
    Represents the properties and constants for Hydrogen Sulfide(H2S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hydrogen Sulfide, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 188, in the equation forms `Component` uses.
    At 25 C and 1 atm hydrogen sulfide is a gas: `specific_heat()` and
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
    name = "Hydrogen Sulfide"
    formula = "H2S"
    # Molecular weight and critical properties: Table 2-141, p. 2-140.
    molecular_weight = 34.081
    # Heat exchanger data, read by Component.hx_data() and httype()
    # Sour gas: wet H2S attacks carbon steel, so it takes the "acid" row.
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "acid"
    _hx_velocity_key = "hydrogen_sulfide"

    # Critical properties
    _critical_temperature = Temperature(373.53, "K")
    _critical_pressure = Pressure(8.963, "MPa")
    _critical_volume = Volume(0.0985, "m3")
    _critical_zc = 0.284
    _critical_acentric_factor = 0.0942

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 187.68-373.53 K: Table 2-32, p. 2-101.
    _density_constants = [2.7672, 0.27369, 373.53, 0.29015]
    # Liquid Cp, Table 2-153, "use Eq. (2)", J/(kmol K), 187.68-370 K:
    # p. 2-168. `specific_heat()` below evaluates Eq. (2).
    _specific_heat_constants = [64.666, 49354, 22.493, -1623, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 187.68-350 K: Table 2-313, p. 2-430.
    _viscosity_constants = [-10.905, 762.11, -0.11863, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 193.15-292.42 K:
    # Table 2-315, p. 2-442.
    _thermal_conductivity_constants = [0.4842, -0.001184, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 187.68-373.53 K: Table 2-8, p. 2-58.
    _vapor_pressure_constants = [85.584, -3839.9, -11.199, 1.8848E-02, 1]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 187.68-373.53 K:
    # Table 2-150, p. 2-153 (C1 x 1E-07 = 2.5676).
    _enthalpy_constants = [2.5676E7, 0.37358, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K: Table 2-156, p. 2-179
    # (C1 = 0.33288E5, C2 = 0.26086E5, C3 = 0.9134E3, C4 = -0.17979E5, C5 = 949.4).
    _ideal_gas_heat_capacity_constants = [0.33288E5, 0.26086E5, 0.9134E3, -0.17979E5, 949.4]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 212.8-600 K:
    # Table 2-314, p. 2-436.
    _vapor_thermal_conductivity_constants = [1.381E-07, 1.8379, -352.09, 46041]

    @PropertyMethod
    def specific_heat(self) -> SpecificHeat:
        if self._specific_heat is not None:
            return self._specific_heat
        cp_gas = self._ideal_gas_specific_heat()
        if cp_gas is not None:
            return cp_gas
        # Liquid: Perry's 8th ed., Table 2-153, Eq. (2), J/(kmol K):
        # Cp = C1^2/t + C2 - 2*C1*C3*t - C1*C4*t^2 - C3^2*t^3/3 - C3*C4*t^4/2 - C4^2*t^5/5
        # with t = 1 - T/Tc.
        C1, C2, C3, C4 = self._specific_heat_constants[:4]
        T = self.temperature.to("K").value
        t = 1 - T / self._critical_temperature.to("K").value
        cp = (C1 ** 2 / t) + C2 - (2 * C1 * C3 * t) - (C1 * C4 * t ** 2) - (C3 ** 2 * t ** 3 / 3) - (C3 * C4 * t ** 4 / 2) - (C4 ** 2 * t ** 5 / 5)
        return SpecificHeat(cp / self.molecular_weight, "J/kgK")
