from .base import Component
from processpi.units import *
class Cyanogen(Component):
    name = "Cyanogen"
    formula = "C2N2​"
    molecular_weight = 52.035
    _critical_temperature = Temperature(400.15, "K")
    _critical_pressure = Pressure(5.98, "MPa") 
    _critical_volume = Volume(0.195, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.351  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.279  # Placeholder for critical acentric factor
    _density_constants = [1.0743,0.20948,400.15,0.20724]
    _specific_heat_constants = [65516,-144.7,0.063229,0,0]
    _viscosity_constants = [-12.086,994.23,0,0,0] 
    _thermal_conductivity_constants = [0.4685, -0.00086594,0,0,0]
    _vapor_pressure_constants = [81.565,-4808.90,-9.3748,1.39E-05, 2] 
    _enthalpy_constants = [3.384E-7,0.3707, 245.25,2.3803, 0]  # Placeholder for enthalpy constants
