from .base import Component, PropertyMethod
from processpi.units import *

class Hydrogen(Component):
    """
    Represents the properties and constants for Hydrogen(H2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hydrogen, which are essential for various process engineering calculations.
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
    name = "Hydrogen"
    formula = "H2"
    molecular_weight = 2.016
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "inert_gas"

    # Critical properties
    _critical_temperature = Temperature(33.19, "K")
    _critical_pressure = Pressure(1.313, "MPa")
    _critical_volume = Volume(0.064147, "m3")
    _critical_zc = 0.305
    _critical_acentric_factor = -0.216

    _density_constants = [5.414, 0.34893, 33.19, 0.2706]
    _specific_heat_constants = [66.653, 6765.90, -123.63, 478.27, 0.0]
    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 250-1500 K:
    # Table 2-156, p. 2-178 (cmpd. no. 183, Hydrogen).
    _ideal_gas_heat_capacity_constants = [0.27617E5, 0.0956E5, 2.466E3, 0.0376E5, 567.6]
    _viscosity_constants = [-11.661, 24.7, -0.261, -4.1e-16, 10.0]
    _thermal_conductivity_constants = [-0.0917, 0.017678, -0.000382, -3.33e-06, 1.03e-07]
    _vapor_pressure_constants = [12.69, -94.896, 1.1125, 0.000329, 2.0]
    _enthalpy_constants = [0.10127e-7, 0.698, -1.817, 1.447,0.0]

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
    