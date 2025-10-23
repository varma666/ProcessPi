from .base import Component
from processpi.units import *
class FormicAcid(Component):
    name = "Formic Acid"
    formula = "CH2O2"
    molecular_weight = 46.026
    _critical_temperature = Temperature(588, "K")
    _critical_pressure = Pressure(5.81, "MPa") 
    _critical_volume = Volume(0.125, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.149  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.3173  # Placeholder for critical acentric factor
    _density_constants = [1.938,0.24225,588,0.24435]
    _specific_heat_constants = [78060,71.54,0,0,0]
    _viscosity_constants = [-48.529,3394.7,5.3903,0,0] 
    _thermal_conductivity_constants = [0.302,-0.000108,0,0,0]
    _vapor_pressure_constants = [50.323,-5378.2,-4.203,0.0000034697,2] 
    _enthalpy_constants = [2.3195E-7,1.9091,-5.0003,3.2641, 0]  # Placeholder for enthalpy constants
