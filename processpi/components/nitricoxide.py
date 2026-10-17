from .base import Component
from processpi.units import *

class NitricOxide(Component):
    """
    Represents the properties and constants for Nitric Oxide(NO).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nitric Oxide, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 253, in the equation forms `Component` uses.
    At 25 C and 1 atm nitric oxide is a gas: `specific_heat()` and
    `thermal_conductivity()` then use the ideal-gas Cp and the vapour k below,
    and `viscosity()` the base class's Sutherland fallback (air constants).
    Nitric oxide is not in Table 2-156, so the ideal-gas Cp is Table 2-155's
    polynomial.

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
    name = "Nitric Oxide"
    formula = "NO"
    # Molecular weight and critical properties: Table 2-141, p. 2-141.
    molecular_weight = 30.006
    # Heat exchanger data, read by Component.hx_data() and httype()
    # An oxidiser, not an inert gas: CORROSION_SEVERITY_DATABASE has no
    # oxidiser row, so it takes the generic low-medium "hydrocarbon" row.
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "nitric_oxide"

    # Critical properties
    _critical_temperature = Temperature(180.15, "K")
    _critical_pressure = Pressure(6.48, "MPa")
    _critical_volume = Volume(0.058, "m3")
    _critical_zc = 0.251
    _critical_acentric_factor = 0.5829

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 109.5-180.15 K: Table 2-32, p. 2-102.
    _density_constants = [5.246, 0.3044, 180.15, 0.242]
    # Liquid Cp, polynomial, J/(kmol K), 109.5-150 K: Table 2-153, p. 2-169.
    _specific_heat_constants = [-2979600, 76602, -652.59, 1.8879, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 109.5-180.05 K: Table 2-313, p. 2-431.
    _viscosity_constants = [-246.65, 3150.3, 49.98, -0.22541, 1]
    # Liquid thermal conductivity, polynomial, W/(m K), 110-176.4 K:
    # Table 2-315, p. 2-443.
    _thermal_conductivity_constants = [0.1878, 0.0010293, -0.00000943, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 109.5-180.15 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [72.974, -2650, -8.261, 9.7000E-15, 6]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 109.5-180.15 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 2.131).
    _enthalpy_constants = [2.131E7, 0.4056, 0, 0, 0]

    # Ideal-gas Cp, polynomial, J/(kmol K), 100-1500 K: Table 2-155, p. 2-175.
    # The row prints C4 = -5.7357 under "C4 x 1E 05" and C5 = 0.0014526 under
    # "C5 x 1E 10"; C5 = 1.4526E-08 is the value that gives the row's own
    # 0.3586E5 at 1500 K (the 1E-13 that the heading implies gives -0.377E5).
    _ideal_gas_heat_capacity_polynomial = [34980, -35.32, 0.07729, -5.7357E-05, 1.4526E-08]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 121.38-750 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [0.0004096, 0.7509, 45.6, 0]

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
