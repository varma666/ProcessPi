from .base import Component
from processpi.units import *
class Chloroform(Component):
    name = "Chloroform"
    formula = "CHCl3​"
    molecular_weight = 119.378
    _critical_temperature = Temperature(536.4, "K")
    _critical_pressure = Pressure(5.472, "MPa") 
    _critical_volume = Volume(0.239, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.293  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2219  # Placeholder for critical acentric factor
    _density_constants = [1.0841,0.2581,536.4,0.2741]
    _specific_heat_constants = [124850,-166.34,0.43209,0,0]
    _viscosity_constants = [-14.109,1049.2,0.5377,0,0] 
    _thermal_conductivity_constants = [0.1778, -0.0002023,0,0,0]
    _vapor_pressure_constants = [146.43,-7792.30,-20.614,2.46E-02, 1] 
    _enthalpy_constants = [4.186E-7,0.3584, 209.63,3.5047, 0]  # Placeholder for enthalpy constants
