from .base import Component
from processpi.units import *
class ChloroBenzene(Component):
    name = "Chloro Benzene"
    formula = "C6​H5​Cl"
    molecular_weight = 112.557
    _critical_temperature = Temperature(632.35, "K")
    _critical_pressure = Pressure(4.519, "MPa") 
    _critical_volume = Volume(0.308, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.265  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2499  # Placeholder for critical acentric factor
    _density_constants = [0.8711,0.26805,632.35,0.2799]
    _specific_heat_constants = [-1307500,15338,-53.974,0.063483,0]
    _viscosity_constants = [0.15772,540.5,-1.6075,1.50E+14,-6.00E+00] 
    _thermal_conductivity_constants = [0.1841, -0.0001917,0,0,0]
    _vapor_pressure_constants = [54.144,-6244.40,-4.5343,4.70E-18, 6] 
    _enthalpy_constants = [5.148E-7,0.36614, 227.95,4.3707, 0]  # Placeholder for enthalpy constants
