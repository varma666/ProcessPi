from .base import Component, PropertyMethod
from processpi.units import *

class Heptane(Component):
    """
    Represents the properties and constants for Heptane(C7H16).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Heptane, which are essential for various process engineering calculations.
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
    name = "Heptane"
    formula = "C7H16"
    molecular_weight = 100.202
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(540.2, "K")
    _critical_pressure = Pressure(2.74, "MPa")
    _critical_volume = Volume(0.428, "m3")
    _critical_zc = 0.261
    _critical_acentric_factor = 0.3495

    _density_constants = [0.61259, 0.26211, 540.2, 0.28141]
    _specific_heat_constants = [61.26, 314410, 1824.60,-2547.90, 0.0]
    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 200-1500 K:
    # Table 2-156, p. 2-178 (cmpd. no. 160, Heptane).
    _ideal_gas_heat_capacity_constants = [1.2015E5, 4.001E5, 1.6766E3, 2.74E5, 756.4]
    _viscosity_constants = [-9.4622, 877.07, -0.23445, 1.4e+22, -10.0]
    _thermal_conductivity_constants = [0.215, -0.000303, 0, 0, 0]
    _vapor_pressure_constants = [87.829, -6996.40, -9.8802, 7.21e-06, 2.0]
    _enthalpy_constants = [5.0014e-7, 0.38795, 0, 0, 0]

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
    
        