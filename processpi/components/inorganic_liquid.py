from .base import Component
from processpi.units import *

class InorganicLiquid(Component):
    name = "Inorganic Liquid"
    formula = "Inorganic"
    molecular_weight = 80.0
    _critical_temperature = Temperature(600, "K")
    _critical_pressure = Pressure(5.0, "MPa")
    _critical_volume = Volume(0.23, "m3")
    _critical_zc = 0.28
    _critical_acentric_factor = 0.2
    _density_constants = [1.4, 0.28, 600, 0.3]
    _specific_heat_constants = [130000, -140, 0.25, 0.0006, 0]
    _viscosity_constants = [-11.5, 950, 0.58, 0, 0]
    _thermal_conductivity_constants = [0.25, -0.00035, 0, 0, 0]
    _vapor_pressure_constants = [65, -6500, -7.1, 0.000006, 2]
    _enthalpy_constants = [4.0E-7, 0.32, 175, 3.4, 0]
