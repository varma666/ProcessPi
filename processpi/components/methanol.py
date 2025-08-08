
from .base import Component
from processpi.units import *


class Methanol(Component):
    name = "Methanol"
    formula = "CH3OH"
    molecular_weight = 32.042
    _critical_temperature = Temperature(512.6, "K")
    _critical_pressure = Pressure(8.1, "MPa")
    _critical_volume = Volume(0.117, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.222  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.5658  # Placeholder for critical acentric factor
    _density_constants = [2.3267, 0.27073, 512.5, 0.24713]
    _specific_heat_constants = [105800,-362.23,0.9379,0,0]
    _viscosity_constants = [-25.317, 1789.2, 2.069, 0, 0] 
    _thermal_conductivity_constants = [0.2837, -0.000281, 0,0,0]
    _vapor_pressure_constants = [82.718, -6904.5, -8.8622, 0.0000074664, 2] 
    _enthalpy_constants = [5.0451e-7, 0.33594, 175.47, 4.3825, 0]  # Placeholder for enthalpy constants
