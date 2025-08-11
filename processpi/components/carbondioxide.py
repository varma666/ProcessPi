from .base import Component
from processpi.units import *


class Carbondioxide(Component):
    name = "Carbon Dioxide"
    formula = "CO2"
    molecular_weight = 44.01
    _critical_temperature = Temperature(304.21, "K")
    _critical_pressure = Pressure(7.383, "MPa") 
    _critical_volume = Volume(0.094, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.274  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2236  # Placeholder for critical acentric factor
    _density_constants = [2.768, 0.26212,304.21,0.2908]
    _specific_heat_constants = [-8304300,104370,-433.33,0.60052,0]
    _viscosity_constants = [18.775,-402.92,-4.6854,-6.92E-26, 10] 
    _thermal_conductivity_constants = [0.4406, -0.0012175,0,0,0]
    _vapor_pressure_constants = [140.54,-4735,-21.268,4.09E-02, 1] 
    _enthalpy_constants = [2.173E-7, 0.382, -0.4339,0.42213, 0]  # Placeholder for enthalpy constants
