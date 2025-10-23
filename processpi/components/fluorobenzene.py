from .base import Component
from processpi.units import *
class FluoroBenzene(Component):
    name = "Fluorobenzene"
    formula = "C6H5F"
    molecular_weight = 96.102
    _critical_temperature = Temperature(560.09, "K")
    _critical_pressure = Pressure(4.551, "MPa") 
    _critical_volume = Volume(0.269, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.263  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2472  # Placeholder for critical acentric factor
    _density_constants = [1.0146,0.27277,560.09,0.28291]
    _specific_heat_constants = [-991200,11734,-40.669,0.047333,0]
    _viscosity_constants = [-10.064,1058.7,-0.17162,0,0] 
    _thermal_conductivity_constants = [0.20962,-0.00028034,0,0,0]
    _vapor_pressure_constants = [51.915,-5439,-4.2896,8.7527E-18,6] 
    _enthalpy_constants = [4.582E-7,0.3717, 0,0, 0]  # Placeholder for enthalpy constants
