from .base import Component
from processpi.units import *
class Ethane(Component):
    name = "Ethane"
    formula = "C2H6​"
    molecular_weight = 30.069
    _critical_temperature = Temperature(305.32, "K")
    _critical_pressure = Pressure(4.872, "MPa") 
    _critical_volume = Volume(0.1455, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.279  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.0995  # Placeholder for critical acentric factor
    _density_constants = [1.9122,0.27937,305.32,0.29187]
    _specific_heat_constants = [44.009,89718,918.77,-1886,0]
    _viscosity_constants = [-7.0046,276.38,-0.6087,-3.11E-18,7] 
    _thermal_conductivity_constants = [0.35758, -0.0011458,6.19E-07,0,0]
    _vapor_pressure_constants = [51.857,-2598.70,-5.1283,1.49E-05, 2] 
    _enthalpy_constants = [2.1091E-7,0.60646, -0.55492,0.32799, 0]  # Placeholder for enthalpy constants

    #@PropertyMethod
    def specific_heat(self) -> SpecificHeat:
        if self._specific_heat is not None:
            return self._specific_heat
        T = self.temperature.value
        Tr = T / self._critical_temperature.value
        t = 1 - Tr
        cp = (self._sepcific_heat_constants[0] / t ) + (self._sepcific_heat_constants[1]) - ( 2 * self._sepcific_heat_constants[0] * self._sepcific_heat_constants[2] * t) - (self._sepcific_heat_constants[0] * self._sepcific_heat_constants[3] * (t**2)) - ((self._sepcific_heat_constants[2]**2)*(t**3)/3) - ((self._sepcific_heat_constants[2] * self._sepcific_heat_constants[3] * (t**4))/2) - ((self._sepcific_heat_constants[0]**2) * (t**5)/5) 
        return SpecificHeat(cp, "J/kgK")
