from .base import Component, PropertyMethod
from processpi.units import *

class _11Difluoroethane(Component):
    """
    Represents the properties and constants for 11Difluoroethane(C2H4F2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 11Difluoroethane, which are essential for various process engineering calculations.
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
    name = "11Difluoroethane"
    formula = "C2H4F2"
    molecular_weight = 66.05
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(386.44, "K")
    _critical_pressure = Pressure(4.52, "MPa")
    _critical_volume = Volume(0.179, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.2751

    _density_constants = [1.4345, 0.25774, 386.44, 0.28178]
    # Liquid Cp, Table 2-153, "use Eq. (2)", J/(kmol K), 154.56-359.98 K:
    # p. 2-166 (C2 = 105,580; it was 0.0 here).
    _specific_heat_constants = [67.155, 105580, 310.21, -490.54, 0.0]
    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 200-1500 K:
    # Table 2-156, p. 2-177 (cmpd. no. 97, 1,1-Difluoroethane).
    _ideal_gas_heat_capacity_constants = [0.49653E5, 1.2546E5, 1.5394E3, 0.87561E5, 694.17]
    _viscosity_constants = [10.501, -52.181, -3.3459, 0.0, 0.0]
    _thermal_conductivity_constants = [0.27019, -0.000661, 3.44e-07, 0.0, 0.0]
    _vapor_pressure_constants = [73.491, -4385.90, -8.1851, 1.3e-05, 2.0]
    _enthalpy_constants = [3.2312e-7, 0.37653, 0.0, 0.0, 0.0]

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
    