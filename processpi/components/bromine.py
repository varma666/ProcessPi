from .base import Component
from processpi.units import *


class Bromine(Component):
    name = "Bromine"
    formula = "Br2"
    molecular_weight = 159.808
    _critical_temperature = Temperature(584.15, "K")
    _critical_pressure = Pressure(10.3, "MPa") 
    _critical_volume = Volume(0.135, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.286  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.129  # Placeholder for critical acentric factor
    _density_constants = [2.1872, 0.29527, 584.15,0.3295]
    _specific_heat_constants = [179400,-667.11,1.0701,0,0]
    _viscosity_constants = [16.775,-314,-3.9763,0, 0] 
    _thermal_conductivity_constants = [-0.2185, 0.0042143,-0.000017753,3.10E-08,-2.01E-11]
    _vapor_pressure_constants = [108.26, -6592, -14.16,1.60E-02, 1] 
    _enthalpy_constants = [4E-7, 0.351, 265.85,3.2323, 0]  # Placeholder for enthalpy constants
