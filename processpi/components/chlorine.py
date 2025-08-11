from .base import Component
from processpi.units import *
class Chlorine(Component):
    name = "Chlorine"
    formula = "Cl2"
    molecular_weight = 70.906
    _critical_temperature = Temperature(417.15, "K")
    _critical_pressure = Pressure(7.71, "MPa") 
    _critical_volume = Volume(0.124, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.276  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.0688  # Placeholder for critical acentric factor
    _density_constants = [2.23,0.27645,417.15,0.2926]
    _specific_heat_constants = [63936,46.35,-0.1623,0,0]
    _viscosity_constants = [-9.5412,456.62,0,0,0] 
    _thermal_conductivity_constants = [0.2246, -0.000064,-0.000000788,0,0]
    _vapor_pressure_constants = [71.334,-3855,-8.5171,1.24E-02, 1] 
    _enthalpy_constants = [3.068E-7, 0.8458, -0.9001,0.453, 0]  # Placeholder for enthalpy constants
