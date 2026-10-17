from .base import Component
from processpi.units import *

class _2Nonanol(Component):
    """
    Represents the properties and constants for 2Nonanol(C9H20O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Nonanol, which are essential for various process engineering calculations.
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
    name = "2Nonanol"
    formula = "C9H20O"
    molecular_weight = 144.255
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(649.5, "K")
    _critical_pressure = Pressure(2.541, "MPa")
    _critical_volume = Volume(0.577, "m3")
    _critical_zc = 0.271
    _critical_acentric_factor = 0.5911

    _density_constants = [0.41687, 0.24056, 649.5, 0.2916]
    _specific_heat_constants = [329641, -1046.78, 3.61823, 0.0, 0.0]
    _viscosity_constants = [-98.854, 7183.8, 12.283, 0.0, 0.0]
    _thermal_conductivity_constants = [0.20829, -0.00022922, 0.0, 0.0, 0.0]
    _vapor_pressure_constants = [146.46, -13813, -17.158, 8.63e-40, 14.0]
    _enthalpy_constants = [7.9797e-7, -1.0341, 3.553, -2.1149]
