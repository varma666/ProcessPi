from .base import Component
from processpi.units import *

class Helium(Component):
    """
    Represents the properties and constants for Helium(He).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Helium, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 157, in the equation forms `Component` uses.
    At 25 C and 1 atm helium is a gas: `specific_heat()` and
    `thermal_conductivity()` then use the ideal-gas Cp and the vapour k below,
    and `viscosity()` the base class's Sutherland fallback (air constants).
    Helium-4 has two liquid Cp rows in Table 2-153; the 2.20-4.60 K row
    (above the lambda point, the range of Table 2-32) is used. Helium is not
    in Table 2-156, so the ideal-gas Cp is Table 2-155's polynomial, which
    is the constant 5/2 R = 20,786 J/(kmol K).

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
    name = "Helium"
    formula = "He"
    # Molecular weight and critical properties: Table 2-141, p. 2-140.
    molecular_weight = 4.003
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "inert_gas"
    _hx_velocity_key = "helium_4"

    # Critical properties
    _critical_temperature = Temperature(5.2, "K")
    _critical_pressure = Pressure(0.2275, "MPa")
    _critical_volume = Volume(0.0573, "m3")
    _critical_zc = 0.302
    _critical_acentric_factor = -0.39

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 2.2-5.2 K: Table 2-32, p. 2-100.
    _density_constants = [7.2475, 0.41865, 5.2, 0.24096]
    # Liquid Cp, polynomial, J/(kmol K), 2.2-4.6 K: Table 2-153, p. 2-167.
    _specific_heat_constants = [387220, -465570, 211800, -42494, 3212.9]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 2.2-5.1 K: Table 2-313, p. 2-429.
    _viscosity_constants = [-9.6312, -3.841, -1.458, -1.065E-08, 10]
    # Liquid thermal conductivity, polynomial, W/(m K), 2.2-4.8 K:
    # Table 2-315, p. 2-441.
    _thermal_conductivity_constants = [-0.013833, 0.022913, -0.0054872, 0.0004585, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 1.76-5.2 K: Table 2-8, p. 2-57.
    _vapor_pressure_constants = [11.533, -8.99, 0.6724, 2.7430E-01, 1]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 2.2-5.2 K:
    # Table 2-150, p. 2-152 (C1 x 1E-07 = 0.012504).
    _enthalpy_constants = [1.2504E5, 1.3038, -2.6954, 1.7098, 0]

    # Ideal-gas Cp, polynomial, J/(kmol K), 100-1500 K: Table 2-155, p. 2-174.
    _ideal_gas_heat_capacity_polynomial = [20786, 0, 0, 0, 0]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 30-2000 K:
    # Table 2-314, p. 2-435.
    _vapor_thermal_conductivity_constants = [0.00226, 0.7305, -18.63, 440]

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
