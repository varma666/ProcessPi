
from .base import Component
from processpi.units import *


class Air(Component):
    name = "Air"
    formula = "Mixture​"
    molecular_weight = 28.96
    _critical_temperature = Temperature(132.45, "K")
    _critical_pressure = Pressure(3.774, "MPa") 
    _critical_volume = Volume(0.09147, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.313  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0  # Placeholder for critical acentric factor
    _density_constants = [0.26733, 132.45, 0.27341,59.15]
    _specific_heat_constants = [-214460,9185.1,-106.12,0.41616,0]
    _viscosity_constants = [-20.077, 285.15, 1.784,-6.2382E-22, 10] 
    _thermal_conductivity_constants = [0.28472, -0.0017393, 0,0,0]
    _vapor_pressure_constants = [21.662, -692.39, -0.392, 0.0047574, 1] 
    _enthalpy_constants = [0.3822E-7, 59.15,0.6759,132.45, 0]  # Placeholder for enthalpy constants
