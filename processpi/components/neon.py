from .base import Component
from processpi.units import *

class Neon(Component):
    """
    Represents the properties and constants for Neon(Ne).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Neon, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 247, in the equation forms `Component` uses.
    At 25 C and 1 atm neon is a gas: `specific_heat()` and
    `thermal_conductivity()` then use the ideal-gas Cp and the vapour k below,
    and `viscosity()` the base class's Sutherland fallback (air constants).
    Neon is not in Table 2-156, so the ideal-gas Cp is Table 2-155's
    polynomial, which is the constant 5/2 R = 20,786 J/(kmol K).

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
    - `_ideal_gas_heat_capacity_polynomial`: Ideal-gas Cp, used in the gas phase.
    - `_vapor_thermal_conductivity_constants`: Vapour thermal conductivity, used
      in the gas phase.
    """
    name = "Neon"
    formula = "Ne"
    # Molecular weight and critical properties: Table 2-141, p. 2-141.
    molecular_weight = 20.180
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "inert_gas"
    _hx_velocity_key = "neon"

    # Critical properties
    _critical_temperature = Temperature(44.4, "K")
    _critical_pressure = Pressure(2.653, "MPa")
    _critical_volume = Volume(0.0417, "m3")
    _critical_zc = 0.3
    _critical_acentric_factor = -0.0396

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 24.56-44.4 K: Table 2-32, p. 2-102.
    _density_constants = [7.3718, 0.3067, 44.4, 0.2786]
    # Liquid Cp, polynomial, J/(kmol K), 24.56-40 K: Table 2-153, p. 2-169.
    _specific_heat_constants = [1034100, -138770, 7154, -162.55, 1.3841]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 25.09-44.13 K: Table 2-313, p. 2-431.
    _viscosity_constants = [-17.945, 115.57, 1.428, -2.14E-17, 10]
    # Liquid thermal conductivity, polynomial, W/(m K), 25-44 K:
    # Table 2-315, p. 2-443.
    _thermal_conductivity_constants = [0.2971, -0.017356, 0.0005911, -0.000007421, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 24.56-44.4 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [29.755, -271.06, -2.6081, 5.2700E-04, 2]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 24.56-44.4 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 0.2389).
    _enthalpy_constants = [2.389E6, 0.3494, 0, 0, 0]

    # Ideal-gas Cp, polynomial, J/(kmol K), 100-1500 K: Table 2-155, p. 2-175.
    _ideal_gas_heat_capacity_polynomial = [20786, 0, 0, 0, 0]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 30-3273.1 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [0.0011385, 0.6646, 8.7, 0]

    def _ideal_gas_specific_heat(self):
        """Ideal-gas Cp from Table 2-155's polynomial, in the gas phase:

            Cp = C1 + C2*T + C3*T^2 + C4*T^3 + C5*T^4

        Cp in J/(kmol K), T in K. The base class evaluates Table 2-156's DIPPR
        Eq. 107, which has no row for this compound.
        """
        if self.phase.value != "gas":
            return None
        T = self.temperature.to("K").value
        cp_kmol = sum(c * T ** i for i, c in enumerate(self._ideal_gas_heat_capacity_polynomial))
        return SpecificHeat(cp_kmol / self.molecular_weight, "J/kgK")
