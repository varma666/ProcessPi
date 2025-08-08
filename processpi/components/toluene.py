
from .base import Component
from processpi.units import *


class Toluene(Component):
    name = "Toluene"
    formula = "C7H8"
    molecular_weight = 92.138
    _critical_temperature = Temperature(591.8, "K")
    _critical_pressure = Pressure(4.1, "MPa")
    _critical_volume = Volume(0.316, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.264  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.264  # Placeholder for critical acentric factor
    _density_constants = [0.8792, 0.27136, 591.75, 0.29241]
    _specific_heat_constants = [140140,-152.3,0.695,0,0]
   
    _viscosity_constants = [-226.08, 6805.7,37.542,-0.060853, 1] 
    _thermal_conductivity_constants = [0.20463, -0.00024252, 0,0,0]
    _vapor_pressure_constants = [76.945, -6729.8, -8.179, 0.0000053017, 2] 
    _enthalpy_constants = [4.9507E-7, 0.37742, 178.18, 4.3246, 0]  # Placeholder for enthalpy constants
    