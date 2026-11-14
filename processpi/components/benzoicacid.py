from .base import Component
from processpi.units import *


class BenzoicAcid(Component):
    name = "Benzoic Acid"
    formula = "C7H6O2"
    molecular_weight = 122.121
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "acid"
    _hx_velocity_key = "benzoic_acid"
    _critical_temperature = Temperature(751, "K")
    _critical_pressure = Pressure(4.47, "MPa") 
    _critical_volume = Volume(0.344, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.246  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.6028  # Placeholder for critical acentric factor
    _density_constants = [0.71587, 0.24812, 751,0.2857]
    _specific_heat_constants = [-5480,647.12,0,0,0]
    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 200-1500 K:
    # Table 2-156, p. 2-176 (cmpd. no. 18, Benzoic acid).
    _ideal_gas_heat_capacity_constants = [0.77594E5, 2.6455E5, 1.7925E3, 2.2382E5, 835.9]
    _viscosity_constants = [-12.947,2557.9,0,0, 0] 
    _thermal_conductivity_constants = [0.2391, -0.0002325, 0,0,0]
    _vapor_pressure_constants = [88.513, -11829, -8.6826, 2.32E-19, 6] 
    _enthalpy_constants = [10.19E-7, 0.478,0,0,0]  # Placeholder for enthalpy constants
