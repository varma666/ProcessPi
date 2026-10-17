from .base import Component
from processpi.units import *

class Undecane(Component):
    """
    Represents the properties and constants for Undecane(C11H24).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Undecane, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    **Properties:**
    - `name`: The common name of the compound.
    - `formula`: The chemical formula.
    - `molecular_weight`: The molar mass in g/mol.
    - `_critical_temperature`: The critical temperature, above which a substance
      cannot exist as a liquid, regardless of pressure.
    - `_critical_pressure`: The critical pressure, the vapor pressure at the
      critical temperature.
    - `_critical_volume`: The critical volume per kmole.
    - `_critical_zc`: The critical compressibility factor.
    - `_critical_acentric_factor`: The acentric factor, a measure of the
      non-sphericity of the molecule.
    - `_density_constants`: Constants for calculating density as a function of temperature.
    - `_specific_heat_constants`: Constants for calculating specific heat capacity as a
      function of temperature.
    - `_viscosity_constants`: Constants for calculating viscosity as a function of
      temperature.
    - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity
      as a function of temperature.
    - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a
      function of temperature using the Antoine equation or similar models.
    - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature.
    """
    name = "Undecane"
    formula = "C11H24"
    molecular_weight = 156.308
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(639.0, "K")
    _critical_pressure = Pressure(1.95, "MPa")
    _critical_volume = Volume(0.685, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.5303

    _density_constants = [0.36703, 0.24876, 639.0, 0.28571]
    _specific_heat_constants = [293980, -114.98, 0.96936, 0.0, 0.0]
    _viscosity_constants = [52.176, -4951.9, -8.5676, 0.0, -2.0]
    _thermal_conductivity_constants = [0.20515, -0.00023933, 0.0, 0.0, 0.0]
    _vapor_pressure_constants = [131.0, -11143, -15.855, 8.19e-06, 2.0]
    _enthalpy_constants = [7.2284e-7, 0.40607, 0.0, 0.0, 0.0]
