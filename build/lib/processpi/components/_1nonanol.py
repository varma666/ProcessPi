from .base import Component
from processpi.units import *

class _1Nonanol(Component):
    """
    Represents the properties and constants for 1Nonanol(C9?H20?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Nonanol, which are essential for various process engineering calculations.
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
    name = "1Nonanol"
    formula = "C9?H20?O"
    molecular_weight = 144.255

    # Critical properties
    _critical_temperature = Temperature(670.9, "K")
    _critical_pressure = Pressure(2.527, "MPa")
    _critical_volume = Volume(0.576, "m3")
    _critical_zc = 0.261
    _critical_acentric_factor = 0.5841

    _density_constants = [0.43682, 0.25161, 670.9, 0.2498]
    _specific_heat_constants = [0.0, 0.0, 476.87, -0.85381, 0.00056246, 3.5059, 4.6494]
    _viscosity_constants = [-39.863, 4089.0, 3.7631]
    _thermal_conductivity_constants = [0.2292, -0.00023]
    _vapor_pressure_constants = [162.854, 0.0, -19.424, 1.07e-17, 6.0]
    _enthalpy_constants = [7.5429, -1.5966, 4.6489, -2.7229]
