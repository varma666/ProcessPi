from .base import Component
from processpi.units import *


class Butane(Component):
    name = "Butane"
    formula = "C4H10"
    molecular_weight = 58.122
    _critical_temperature = Temperature(425.12, "K")
    _critical_pressure = Pressure(3.796, "MPa") 
    _critical_volume = Volume(0.255, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.274  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2002  # Placeholder for critical acentric factor
    _density_constants = [1.0677, 0.27188,425.12,0.28688]
    _specific_heat_constants = [191030,-1675,12.5,-0.03874,4.61E-05]
    _viscosity_constants = [-7.2471,534.82,-0.57469,-4.66E-27, 0] 
    _thermal_conductivity_constants = [0.27349, -0.00071267,5.16E-07,0,0]
    _vapor_pressure_constants = [66.343,-4363.20,-7.046,9.45E-06, 2] 
    _enthalpy_constants = [3.6238E-7, 0.8337, -0.82274,0.39613, 0]  # Placeholder for enthalpy constants
