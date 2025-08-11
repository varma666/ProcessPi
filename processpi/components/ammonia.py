from .base import Component
from processpi.units import *


class Ammonia(Component):
    name = "Ammonia"
    formula = "NH3"
    molecular_weight = 17.031
    _critical_temperature = Temperature(405.65, "K")
    _critical_pressure = Pressure(11.28, "MPa") 
    _critical_volume = Volume(0.07247, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.242  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2526  # Placeholder for critical acentric factor
    _density_constants = [3.5383, 0.25443, 405.65, 0.2888]
    _specific_heat_constants = [61.289,80925,799.4,-2651,0]
    _viscosity_constants = [-6.743,598.3,-0.7341,-3.69E-27, 10] 
    _thermal_conductivity_constants = [1.169, -0.002314, 0,0,0]
    _vapor_pressure_constants = [90.483, -4,669.70, -11.607, 1.72E-02, 1] 
    _enthalpy_constants = [3.1523E-7, 0.3914, -0.2289,0.2309, 0]  # Placeholder for enthalpy constants
