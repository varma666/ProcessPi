from .base import Component
from processpi.units import *

class HexanoicAcid(Component):
    """
    Represents the properties and constants for Hexanoic acid(C6H12O2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hexanoic acid, which are essential for various process engineering calculations.
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
    name = "Hexanoic acid"
    formula = "C6H12O2"
    molecular_weight = 116.158
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "acid"

    # Critical properties
    _critical_temperature = Temperature(660.2, "K")
    _critical_pressure = Pressure(3.308, "MPa")
    _critical_volume = Volume(0.408, "m3")
    _critical_zc = 0.246
    _critical_acentric_factor = 0.7299

    _density_constants = [0.62833, 0.25598, 660.2, 0.25304]
    _specific_heat_constants = [161980, 44.116, 0.709, 0.0, 0.0]
    _viscosity_constants = [-46.402, 3448.6, 5.0849, 0, 0]
    _thermal_conductivity_constants = [0.1855, -0.000146, 0, 0, 0]
    _vapor_pressure_constants = [114.05, -12332, -12.45, 5.63e-18, 6.0]
    _enthalpy_constants = [9.0746e-7, 0.8926, -0.75172, 0.34378]
