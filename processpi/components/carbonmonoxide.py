from .base import Component
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
    _specific_heat_constants = [65.429,28723,-847.39,1,959.60,0]
    _viscosity_constants = [-4.9735,97.67,-1.1088,0, 0] 
    _thermal_conductivity_constants = [0.2855, -0.001784,0,0,0]
    _vapor_pressure_constants = [45.698,-1076.60,-4.8814,7.57E-05, 2] 
    _enthalpy_constants = [0.8585E-7, 0.4921, -0.326,0.2231, 0]  # Placeholder for enthalpy constants
