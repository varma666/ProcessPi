from .base import Component
from processpi.units import *

class OrganicLiquid(Component):
    name = "Organic Liquid"
    formula = "R-CH"
    molecular_weight = 100.0
    _critical_temperature = Temperature(550, "K")
    _critical_pressure = Pressure(4.5, "MPa")
    _critical_volume = Volume(0.25, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.25
    _density_constants = [1.2, 0.25, 550, 0.3]
    _specific_heat_constants = [140000, -150, 0.28, 0.0007, 0]
    _viscosity_constants = [-12.5, 1000, 0.6, 0, 0]
    _thermal_conductivity_constants = [0.2, -0.0003, 0, 0, 0]
    _vapor_pressure_constants = [70, -6000, -7.0, 0.000006, 2]
    _enthalpy_constants = [4.2E-7, 0.3, 180, 3.5, 0]
