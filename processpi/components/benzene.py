
from .base import Component
from processpi.units import *


class Benzene(Component):
    name = "Benzene"
    formula = "C6H6"
    molecular_weight = 78.114
    _critical_temperature = Temperature(562.1, "K")
    _critical_pressure = Pressure(4.895, "MPa")
    _critical_volume = Volume(0.256, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.268  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2103  # Placeholder for critical acentric factor
    _density_constants = [1.0259, 0.26666, 562.05, 0.28394]
    _specific_heat_constants_1 = [129440,-169.5,0.64781,0,0]
    _specific_heat_constants_2 = [162940,-344.94,0.85562,0,0]
    _viscosity_constants = [7.5117, 294.68,-2.794, 0, 0] 
    _thermal_conductivity_constants = [0.23444, -0.00030572, 0,0,0]
    _vapor_pressure_constants = [83.107, -6486.2, -9.2194, 0.0000069844, 2] 
    _enthalpy_constants = [4.5346E-7, 0.39053, 278.68, 3.4705, 0]  # Placeholder for enthalpy constants
    def specific_heat(self, temperature: Temperature):
        """Return specific heat in kJ/kg.K as a function of temperature in °C"""
        Tr = temperature.value / self._critical_temperature.value
        T = temperature.value
        # Using a polynomial fit for specific heat as a function of reduced temperature
        if T <= 353.24:
            constants = self._specific_heat_constants_1
        else:
            constants = self._specific_heat_constants_2
        
        cp = (constants[0] +
              constants[1] * T +
              constants[2] * T**2 +
              constants[3] * T**3 +
              constants[4] * T**4)
        # Convert to kJ/kg.K
        #cp /= 1000.0
        cp = cp * self.molecular_weight
        return SpecificHeat(cp, "J/kgK")
