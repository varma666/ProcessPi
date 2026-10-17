from .base import Component
from processpi.units import *

class _1Undecanol(Component):
    """
    Represents the properties and constants for 1Undecanol(C11H24O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Undecanol, which are essential for various process engineering calculations.
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
    name = "1Undecanol"
    formula = "C11H24O"
    molecular_weight = 172.308
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(703.9, "K")
    _critical_pressure = Pressure(2.119, "MPa")
    _critical_volume = Volume(0.715, "m3")
    _critical_zc = 0.259
    _critical_acentric_factor = 0.6236

    _density_constants = [0.33113, 0.23676, 703.9, 0.2762]
    _specific_heat_constants = [129450, -3039.50, 27.927, -0.061847, 4.3e-05]
    _viscosity_constants = [-69.778, 5905.2, 8.0214,0,0]
    _thermal_conductivity_constants = [0.21211, -0.00021815,0,0,0]
    _vapor_pressure_constants = [182.571, -17112, -22.125, 1.13e-17, 6.0]
    _enthalpy_constants = [8.7274e-7, -1.5834, 5.0913, -3.2171,0]
