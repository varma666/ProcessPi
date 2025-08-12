from .base import Component
from processpi.units import *
class ChloroMethane(Component):
    name = "Chloro Methane"
    formula = "CH3Cl​"
    molecular_weight = 50.488
    _critical_temperature = Temperature(416.25, "K")
    _critical_pressure = Pressure(6.68, "MPa") 
    _critical_volume = Volume(0.143, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.276  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.1531  # Placeholder for critical acentric factor
    _density_constants = [1.817,0.25877,416.25,0.2833]
    _specific_heat_constants = [96910,-207.9,0.37456,0.000488,0]
    _viscosity_constants = [-25.132,1381.9,2.0811,-4.50E-27,10] 
    _thermal_conductivity_constants = [0.41067, -0.0008478,0,0,0]
    _vapor_pressure_constants = [64.697,-4048.10,-6.8066,1.04E-05, 2] 
    _enthalpy_constants = [2.9745E-7,0.353, 175.43,2.452, 0]  # Placeholder for enthalpy constants
