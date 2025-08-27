from .base import Component
from processpi.units import *

class Oil(Component):
    name = "Generic Oil"
    formula = "Hydrocarbon Oil"
    molecular_weight = 150.0
    _critical_temperature = Temperature(650, "K")
    _critical_pressure = Pressure(3.0, "MPa")
    _critical_volume = Volume(0.3, "m3")
    _critical_zc = 0.25
    _critical_acentric_factor = 0.4
    _density_constants = [1.1, 0.3, 650, 0.3]
    _specific_heat_constants = [180000, -200, 0.35, 0.0008, 0]
    _viscosity_constants = [-10.0, 1100, 0.7, 0, 0]
    _thermal_conductivity_constants = [0.18, -0.00025, 0, 0, 0]
    _vapor_pressure_constants = [75, -7000, -7.2, 0.000007, 2]
    _enthalpy_constants = [4.5E-7, 0.34, 200, 3.6, 0]
