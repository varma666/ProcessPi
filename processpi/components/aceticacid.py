from .base import Component
from processpi.units import *


class AceticAcid(Component):
    name = "Acetic Acid"
    formula = "CH3COOH"
    molecular_weight = 60.052
    _critical_temperature = Temperature(591.95, "K")
    _critical_pressure = Pressure(5.786, "MPa") 
    _critical_volume = Volume(0.177, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.208  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.4665  # Placeholder for critical acentric factor
    _density_constants = [1.4486, 0.25892, 591.95, 0.2529]
    _specific_heat_constants = [139640,-320.8,0.8985,0,0]
    _viscosity_constants = [-9.03, 1212.3, -0.322, 0, 0] 
    _thermal_conductivity_constants = [0.214, -0.0001834, 0,0,0]
    _vapor_pressure_constants = [53.27, -6304.5, -4.2985, 8.8865E-18, 6] 
    _enthalpy_constants = [4.0179E-7, 2.6037, -5.0031,2.7069, 0]  # Placeholder for enthalpy constants
