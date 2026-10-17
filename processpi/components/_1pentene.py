from .base import Component
from processpi.units import *

class _1Pentene(Component):
    """
    Represents the properties and constants for 1Pentene(C5H10).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Pentene, which are essential for various process engineering calculations.
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
    name = "1Pentene"
    formula = "C5H10"
    molecular_weight = 70.133
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(464.8, "K")
    _critical_pressure = Pressure(3.56, "MPa")
    _critical_volume = Volume(0.293, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.2372

    _density_constants = [0.89816, 0.26608, 464.8, 0.28571]
    _specific_heat_constants = [156100, -456.94, 2.255, -0.003163, 2.38e-06]
    _viscosity_constants = [-10.667, 659.56,0,0,0]
    _thermal_conductivity_constants = [0.21361, -0.00030777,0,0,0]
    _vapor_pressure_constants = [46.994, -4289.50, -3.7345, 2.54e-17, 6.0]
    _enthalpy_constants = [3.5027e-7, 0.3481, -0.19672, 0.22394,0]
