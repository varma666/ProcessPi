from .base import Component, PropertyMethod
from processpi.units import *

class _13Butanediol(Component):
    """
    Represents the properties and constants for 13Butanediol(C4H10O2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 13Butanediol, which are essential for various process engineering calculations.
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
    name = "13Butanediol"
    formula = "C4H10O2"
    molecular_weight = 90.121
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(676.0, "K")
    _critical_pressure = Pressure(4.02, "MPa")
    _critical_volume = Volume(0.305, "m3")
    _critical_zc = 0.218
    _critical_acentric_factor = 0.7043

    _density_constants = [0.81856, 0.24967, 676.0, 0.22023]
    # Liquid Cp, Perry's Chemical Engineers' Handbook, 8th ed., Table 2-153,
    # p. 2-165, "use Eq. (2)", 196.15-670 K (see specific_heat below).
    _specific_heat_constants = [42.152,324580,517.35,1449.50,0]
    _viscosity_constants = [-390.03, 18609.0, 60.014, -0.055844, 1.0]
    _thermal_conductivity_constants = [-0.0032865, 0.0011463, -1.55e-06,0,0]
    _vapor_pressure_constants = [123.22, -12620, -13.986, 3.93e-06, 2.0]
    _enthalpy_constants = [9.2247e-7, 0.42442,0,0,0]


    @PropertyMethod
    def specific_heat(self) -> SpecificHeat:
        if self._specific_heat is not None:
            return self._specific_heat
        # Liquid: Perry's 8th ed., Table 2-153, Eq. (2), J/(kmol K):
        # Cp = C1^2/t + C2 - 2*C1*C3*t - C1*C4*t^2 - C3^2*t^3/3 - C3*C4*t^4/2 - C4^2*t^5/5
        # with t = 1 - T/Tc. Gives the table's 0.6251E5 at 196.15 K and 5.2437E5 at 670 K.
        C1, C2, C3, C4 = self._specific_heat_constants[:4]
        T = self.temperature.to("K").value
        t = 1 - T / self._critical_temperature.to("K").value
        cp = (C1 ** 2 / t) + C2 - (2 * C1 * C3 * t) - (C1 * C4 * t ** 2) - (C3 ** 2 * t ** 3 / 3) - (C3 * C4 * t ** 4 / 2) - (C4 ** 2 * t ** 5 / 5)
        return SpecificHeat(cp / self.molecular_weight, "J/kgK")

