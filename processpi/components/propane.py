from .base import Component, PropertyMethod
from processpi.units import *

class Propane(Component):
    """
    Represents the properties and constants for Propane(C3H8).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Propane, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 295, in the equation forms `Component` uses.
    At 25 C and 1 atm propane is a gas: `specific_heat()` and
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
    name = "Propane"
    formula = "C3H8"
    # Molecular weight and critical properties: Table 2-141, p. 2-142.
    molecular_weight = 44.096
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "propane"

    # Critical properties
    _critical_temperature = Temperature(369.83, "K")
    _critical_pressure = Pressure(4.248, "MPa")
    _critical_volume = Volume(0.2, "m3")
    _critical_zc = 0.276
    _critical_acentric_factor = 0.1523

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 85.47-369.83 K: Table 2-32, p. 2-102.
    _density_constants = [1.3757, 0.27453, 369.83, 0.29359]
    # Liquid Cp, Table 2-153, "use Eq. (2)", J/(kmol K), 85.47-360 K:
    # p. 2-169. `specific_heat()` below evaluates Eq. (2).
    _specific_heat_constants = [62.983, 113630, 633.21, -873.46, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 85.47-360 K: Table 2-313, p. 2-431.
    _viscosity_constants = [-17.156, 646.25, 1.1101, -7.3439E-11, 4]
    # Liquid thermal conductivity, polynomial, W/(m K), 85.47-350 K:
    # Table 2-315, p. 2-443.
    _thermal_conductivity_constants = [0.26755, -0.00066457, 2.774E-07, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 85.47-369.83 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [59.078, -3492.6, -6.0669, 1.0919E-05, 2]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 85.47-369.83 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 2.9209).
    _enthalpy_constants = [2.9209E7, 0.78237, -0.77319, 0.39246, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 200-1500 K: Table 2-156, p. 2-180
    # (C1 = 0.5192E5, C2 = 1.9245E5, C3 = 1.6265E3, C4 = 1.168E5, C5 = 723.6).
    _ideal_gas_heat_capacity_constants = [0.5192E5, 1.9245E5, 1.6265E3, 1.168E5, 723.6]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 231.11-1000 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [-1.12, 0.10972, -9834.6, -7535800]

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
