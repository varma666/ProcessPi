from .base import Component
from processpi.units import *

class Vapor(Component):
    name = "Generic Vapor"
    formula = "Gas"
    molecular_weight = 28.0
    _critical_temperature = Temperature(400, "K")
    _critical_pressure = Pressure(3.8, "MPa")
    _critical_volume = Volume(0.3, "m3")
    _critical_zc = 0.29
    _critical_acentric_factor = 0.1
    _density_constants = [1.0, 0.25, 400, 0.28]
    _specific_heat_constants = [1000, 0, 0, 0, 0]
    _viscosity_constants = [-10.5, 800, 0.55, 0, 0]
    _thermal_conductivity_constants = [0.015, 0, 0, 0, 0]
    _vapor_pressure_constants = [50, -5000, -6.8, 0.000005, 2]
    _enthalpy_constants = [3.5E-7, 0.28, 150, 3.2, 0]
