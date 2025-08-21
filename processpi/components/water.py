from .base import Component
from processpi.units import *
from math import *

class Water(Component):
    name = "Water"
    formula = "H2O"
    molecular_weight = 18.015
    _critical_temperature = Temperature(647.096, "K")
    _critical_pressure = Pressure(22.06, "MPa")
    _density_constants = [-13.851, 0.654, -0.00191, 0.000002]
    _specific_heat_constants = [276370,-2090.10,8.125,-0.014116,9.37e-6]
    _viscosity_constants = [-52.843, 3703.6, 5.866, -5.879e-29, 10] 
    _thermal_conductivity_constants = [-0.432, 0.0057255, -0.000008078,1.861E-09,0]
    _vapor_pressure_constants = [73.649, -7258.2, -7.3037, 4.1653E-06, 2] 
    _enthalpy_constants = [5.2053E-7, 0.3199, -0.212, 0.25795, 0]

    def density(self, temperature: Temperature = None) -> Density:
        temperature = temperature or self.temperature
        Tr = temperature.value / self._critical_temperature.value
        tou = 1 - Tr
        den = 17.863 + (58.606 * (tou**0.35)) -  (95.396 * (tou**(2/3))) + (213.89 * tou) - (141.26 * (tou**(4/3)))
        den = den * self.molecular_weight
        return Density(den, "kg/m3")
