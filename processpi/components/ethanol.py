
from .base import Component
from processpi.units import *


class Ethanol(Component):
    name = "Ethanol"
    formula = "C2H5OH"
    molecular_weight = 46.068
    _critical_temperature = Temperature(514.00, "K")
    _critical_pressure = Pressure(6.137, "MPa") 
    _critical_volume = Volume(0.168, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.241  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.6436  # Placeholder for critical acentric factor
    _density_constants = [1.6288, 0.27469, 514, 0.23178]
    _specific_heat_constants = [102640,-139.63,-0.030341,0.0020386,0]
    _viscosity_constants = [7.875, 781.98, -3.0418, 0, 0] 
    _thermal_conductivity_constants = [0.2468, -0.000264, 0,0,0]
    _vapor_pressure_constants = [73.304, -7122.3, -7.1424, 0.0000028853, 2] 
    _enthalpy_constants = [5.5789E-7, 0.31245, 159.05, 4.9694, 0]  # Placeholder for enthalpy constants
