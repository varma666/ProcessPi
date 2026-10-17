import warnings

from .base import Component
from processpi.units import *
class Ethylene(Component):
    name = "Ethylene"
    formula = "C2H4"
    molecular_weight = 28.053
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "ethylene"
    _critical_temperature = Temperature(282.34, "K")
    _critical_pressure = Pressure(5.41, "MPa") 
    _critical_volume = Volume(0.131, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.281  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.0862  # Placeholder for critical acentric factor
    _density_constants = [2.0961,0.27657,282.34,0.29174]
    _specific_heat_constants = [247390,-4428,40.936,-0.1697,0.00026816]
    _viscosity_constants = [1.8878,78.865,-2.1554,0,0] 
    _thermal_conductivity_constants = [0.4194,-0.001591,0.000001306,0,0]
    _vapor_pressure_constants = [53.963,-2443,-5.5643,0.000019079,2] 
    _enthalpy_constants = [1.8844E-7,0.36485, 0,0, 0]  # Placeholder for enthalpy constants


class Ethlylene(Ethylene):
    """Misspelt old name of `Ethylene`, kept so existing code still runs."""

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Ethlylene is deprecated; use Ethylene.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
