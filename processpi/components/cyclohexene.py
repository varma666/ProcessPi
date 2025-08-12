from .base import Component
from processpi.units import *
class Cyclohexane(Component):
    name = "Cyclohexane"
    formula = "C6H12​"
    molecular_weight = 84.159
    _critical_temperature = Temperature(553.8, "K")
    _critical_pressure = Pressure(4.08, "MPa") 
    _critical_volume = Volume(0.308, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.273  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2081  # Placeholder for critical acentric factor
    _density_constants = [0.88998,0.27376,553.8,0.28571]
    _specific_heat_constants = [-220600,3118.30,-9.4216,0.010687,0]
    _viscosity_constants = [-33.763,2497.2,3.2236,0,0] 
    _thermal_conductivity_constants = [0.19813, -0.0002505,0,0,0]
    _vapor_pressure_constants = [51.087,-5226.40,-4.2278,19.76E-18, 6] 
    _enthalpy_constants = [4.4902E-7,0.39881, 279.69,3.392, 0]  # Placeholder for enthalpy constants
