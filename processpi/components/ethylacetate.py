import warnings

from .base import Component
from processpi.units import *
class EthylAcetate(Component):
    name = "Ethyl Acetate"
    formula = "C4H8O2"
    molecular_weight = 88.105
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "ethyl_acetate"
    _critical_temperature = Temperature(523.3, "K")
    _critical_pressure = Pressure(3.88, "MPa") 
    _critical_volume = Volume(0.286, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.255  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.3664  # Placeholder for critical acentric factor
    _density_constants = [0.8996,0.25856,523.3,0.278]
    _specific_heat_constants = [226230,-624.8,1.472,0,0]
    _viscosity_constants = [14.354,-154.6,-3.7887,0,0] 
    _thermal_conductivity_constants = [0.2501, -0.0003563,0,0,0]
    _vapor_pressure_constants = [66.824,-6227.60,-6.41,1.79E-17, 6] 
    _enthalpy_constants = [4.933E-7,0.3847, 0,0, 0]  # Placeholder for enthalpy constants


class EthlylAcetate(EthylAcetate):
    """Misspelt old name of `EthylAcetate`, kept so existing code still runs."""

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "EthlylAcetate is deprecated; use EthylAcetate.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
