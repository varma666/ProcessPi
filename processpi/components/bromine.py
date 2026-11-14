from .base import Component
from processpi.units import *


class Bromine(Component):
    name = "Bromine"
    formula = "Br2"
    molecular_weight = 159.808
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "acid"
    _hx_velocity_key = "bromine"
    _critical_temperature = Temperature(584.15, "K")
    _critical_pressure = Pressure(10.3, "MPa") 
    _critical_volume = Volume(0.135, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.286  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.129  # Placeholder for critical acentric factor
    _density_constants = [2.1872, 0.29527, 584.15,0.3295]
    _specific_heat_constants = [179400,-667.11,1.0701,0,0]
    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K:
    # Table 2-156, p. 2-176 (cmpd. no. 25, Bromine).
    _ideal_gas_heat_capacity_constants = [0.30113E5, 0.08009E5, 0.7514E3, 0.1078E5, 314.6]
    _viscosity_constants = [16.775,-314,-3.9763,0, 0] 
    _thermal_conductivity_constants = [-0.2185, 0.0042143,-0.000017753,3.10E-08,-2.01E-11]
    _vapor_pressure_constants = [108.26, -6592, -14.16,1.60E-02, 1] 
    _enthalpy_constants = [4E-7, 0.351, 0,0, 0]  # Placeholder for enthalpy constants
