from .base import Component
from processpi.units import *
class Ethlylene(Component):
    name = "Fluorine"
    formula = "F2"
    molecular_weight = 37.997
    _critical_temperature = Temperature(144.12, "K")
    _critical_pressure = Pressure(5.172, "MPa") 
    _critical_volume = Volume(0.066547, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.287  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.053  # Placeholder for critical acentric factor
    _density_constants = [4.2895,0.28587,144.12,0.28776]
    _specific_heat_constants = [-94585,7529.9,-139.6,1.1301,-0.0033241]
    _viscosity_constants = [8.18,-75.6,-3.5148,0,0] 
    _thermal_conductivity_constants = [0.2758,-0.0016297,0,0,0]
    _vapor_pressure_constants = [42.393,-1103.3,-4.1203,0.000057815,2] 
    _enthalpy_constants = [0.88757E-7,0.34072, 0,0, 0]  # Placeholder for enthalpy constants
