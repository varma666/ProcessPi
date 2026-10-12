from .base import Component, PropertyMethod
from processpi.units import *
class CarbonMonoxide(Component):
    name = "Carbon Monoxide"
    formula = "CO"
    molecular_weight = 28.01
    _critical_temperature = Temperature(132.92, "K")
    _critical_pressure = Pressure(3.499, "MPa") 
    _critical_volume = Volume(0.0944, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.299  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.0482  # Placeholder for critical acentric factor
    _density_constants = [2.897, 0.27532,132.92,0.2813]
    # Liquid Cp, Perry's Chemical Engineers' Handbook, 8th ed., Table 2-153,
    # p. 2-165, "use Eq. (2)", 68.15-132 K. C4 is 1,959.6; the thousands comma
    # had split it into 1 and 959.60.
    _specific_heat_constants = [65.429,28723,-847.39,1959.6,0]
    _viscosity_constants = [-4.9735,97.67,-1.1088,0, 0] 
    _thermal_conductivity_constants = [0.2855, -0.001784,0,0,0]
    _vapor_pressure_constants = [45.698,-1076.60,-4.8814,7.57E-05, 2] 
    _enthalpy_constants = [0.8585E-7, 0.4921, -0.326,0.2231, 0]  # Placeholder for enthalpy constants

    # `_thermal_conductivity_constants` above are the LIQUID CO correlation
    # (Perry's 8th ed., Table 2-315, p. 2-439, 68.15-125 K); it turns negative
    # above 160 K. In the gas phase the base class uses these instead:
    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 60-1500 K: Perry's 8th ed.,
    # Table 2-156, p. 2-176 (C1 = 0.29108E5, C2 = 0.08773E5, C3 = 3.0851E3,
    # C4 = 0.084553E5, C5 = 1538.2). 1040.3 J/kgK at 300 K.
    _ideal_gas_heat_capacity_constants = [0.29108E5, 0.08773E5, 3.0851E3, 0.084553E5, 1538.2]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 70-1500 K: Perry's
    # 8th ed., Table 2-314, p. 2-433. 0.0251 W/mK at 300 K.
    _vapor_thermal_conductivity_constants = [0.00059882, 0.6863, 57.13, 501.92]


    @PropertyMethod
    def specific_heat(self) -> SpecificHeat:
        if self._specific_heat is not None:
            return self._specific_heat
        cp_gas = self._ideal_gas_specific_heat()
        if cp_gas is not None:
            return cp_gas
        # Liquid: Perry's 8th ed., Table 2-153, Eq. (2), J/(kmol K):
        # Cp = C1^2/t + C2 - 2*C1*C3*t - C1*C4*t^2 - C3^2*t^3/3 - C3*C4*t^4/2 - C4^2*t^5/5
        # with t = 1 - T/Tc. Gives the table's 0.5912E5 at 68.15 K.
        C1, C2, C3, C4 = self._specific_heat_constants[:4]
        T = self.temperature.to("K").value
        t = 1 - T / self._critical_temperature.to("K").value
        cp = (C1 ** 2 / t) + C2 - (2 * C1 * C3 * t) - (C1 * C4 * t ** 2) - (C3 ** 2 * t ** 3 / 3) - (C3 * C4 * t ** 4 / 2) - (C4 ** 2 * t ** 5 / 5)
        return SpecificHeat(cp / self.molecular_weight, "J/kgK")
