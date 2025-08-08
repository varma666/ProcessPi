
from .base import Component
from processpi.units import *


class Acetone(Component):
    name = "Acetone"
    formula = "C3H6O"
    molecular_weight = 58.080
    _critical_temperature = Temperature(508.1, "K")
    _critical_pressure = Pressure(4.701, "MPa")
    _critical_volume = Volume(0.209, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.233  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.3065  # Placeholder for critical acentric factor
    _density_constants = [1.2332, 0.25886, 508.2, 0.2913]
    _specific_heat_constants = [135600,-177,0.2837,0.000689,0]
    _viscosity_constants = [-14.918, 1023.4, 0.5961, 0, 0] 
    _thermal_conductivity_constants = [0.2878, -0.000427, 0,0,0]
    _vapor_pressure_constants = [69.006, -5599.6, -7.0985, 0.0000062237, 2] 
    _enthalpy_constants = [4.215E-7, 0.3397, 178.45, 3.639, 0]  # Placeholder for enthalpy constants
