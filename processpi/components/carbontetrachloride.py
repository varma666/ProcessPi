from .base import Component
from processpi.units import *
class CarbonTetrachloride(Component):
    name = "Carbon Tetrachloride"
    formula = "CO"
    molecular_weight = 153.823
    _critical_temperature = Temperature(556.35, "K")
    _critical_pressure = Pressure(4.56, "MPa") 
    _critical_volume = Volume(0.276, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.272  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.1926  # Placeholder for critical acentric factor
    _density_constants = [0.99835, 0.274,556.35,0.287]
    _specific_heat_constants = [-752700,8966.10,-30.394,0.034455,0]
    _viscosity_constants = [-8.0738,1121.1,-0.4726,0, 0] 
    _thermal_conductivity_constants = [0.1589, -0.0001987,0,0,0]
    _vapor_pressure_constants = [78.441,-6128.10,-8.5766,6.85E-06, 2] 
    _enthalpy_constants = [4.3252E-7, 0.37688, 250.33,3.4528, 0]  # Placeholder for enthalpy constants
