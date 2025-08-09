from .base import Component
from processpi.units import *


class AcrylicAcid(Component):
    name = "Acrylic Acid"
    formula = "C3​H4​O2​"
    molecular_weight = 72.063
    _critical_temperature = Temperature(615, "K")
    _critical_pressure = Pressure(5.66, "MPa") 
    _critical_volume = Volume(0.208, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.23  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.5383  # Placeholder for critical acentric factor
    _density_constants = [1.2414, 0.25822, 615,0.30701]
    _specific_heat_constants = [55300,300,0,0,0]
    _viscosity_constants = [-28.12, 2280.2, 2.3956, 0, 0] 
    _thermal_conductivity_constants = [0.2441, -0.0002904, 0,0,0]
    _vapor_pressure_constants = [46.745, -6587.1, -3.2208, 0.00000052253, 2] 
    _enthalpy_constants = [0, 0, 0,0, 0]  # Placeholder for enthalpy constants
