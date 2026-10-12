from .base import Component, PropertyMethod
from processpi.units import *
class Ethane(Component):
    name = "Ethane"
    formula = "C2H6"
    molecular_weight = 30.069
    _critical_temperature = Temperature(305.32, "K")
    _critical_pressure = Pressure(4.872, "MPa") 
    _critical_volume = Volume(0.1455, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.279  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.0995  # Placeholder for critical acentric factor
    _density_constants = [1.9122,0.27937,305.32,0.29187]
    # Liquid Cp, Perry's Chemical Engineers' Handbook, 8th ed., Table 2-153,
    # p. 2-167, "use Eq. (2)", 92-290 K (see specific_heat below).
    _specific_heat_constants = [44.009,89718,918.77,-1886,0]
    _viscosity_constants = [-7.0046,276.38,-0.6087,-3.11E-18,7] 
    _thermal_conductivity_constants = [0.35758, -0.0011458,6.19E-07,0,0]
    _vapor_pressure_constants = [51.857,-2598.70,-5.1283,1.49E-05, 2] 
    _enthalpy_constants = [2.1091E-7,0.60646, -0.55492,0.32799, 0]  # Placeholder for enthalpy constants

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 200-1500 K, used by the base
    # class in the gas phase: Perry's 8th ed., Table 2-156, p. 2-178
    # (C1 = 0.40326E5, C2 = 1.3422E5, C3 = 1.6555E3, C4 = 0.73223E5, C5 = 752.87).
    # 1750.1 J/kgK at 300 K.
    _ideal_gas_heat_capacity_constants = [0.40326E5, 1.3422E5, 1.6555E3, 0.73223E5, 752.87]

    @PropertyMethod
    def specific_heat(self) -> SpecificHeat:
        if self._specific_heat is not None:
            return self._specific_heat
        cp_gas = self._ideal_gas_specific_heat()
        if cp_gas is not None:
            return cp_gas
        # Liquid: Perry's 8th ed., Table 2-153, Eq. (2), J/(kmol K):
        # Cp = C1^2/t + C2 - 2*C1*C3*t - C1*C4*t^2 - C3^2*t^3/3 - C3*C4*t^4/2 - C4^2*t^5/5
        # with t = 1 - T/Tc. Gives the table's 0.6855E5 at 92 K and 1.2444E5 at 290 K.
        C1, C2, C3, C4 = self._specific_heat_constants[:4]
        T = self.temperature.to("K").value
        t = 1 - T / self._critical_temperature.to("K").value
        cp = (C1 ** 2 / t) + C2 - (2 * C1 * C3 * t) - (C1 * C4 * t ** 2) - (C3 ** 2 * t ** 3 / 3) - (C3 * C4 * t ** 4 / 2) - (C4 ** 2 * t ** 5 / 5)
        return SpecificHeat(cp / self.molecular_weight, "J/kgK")
