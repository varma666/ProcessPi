from .base import Component
from processpi.units import *

class AceticAnhydride(Component):
    """
    Represents the properties and constants for Acetic anhydride(C4H6O3).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acetic anhydride, which are essential for various process engineering calculations.
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
    name = "Acetic anhydride"
    formula = "C4H6O3"
    molecular_weight = 102.089

    # Critical properties
    _critical_temperature = Temperature(606.0, "K")
    _critical_pressure = Pressure(4.0, "MPa")
    _critical_volume = Volume(0.29, "m3")
    _critical_zc = 0.23
    _critical_acentric_factor = 0.4535

    _density_constants = [0.86852, 0.25187, 606.0, 0.31172]
    _specific_heat_constants = [36600,511,0,0,0]
    _viscosity_constants = [-14.164, 1350.3, 0.4492,0,0]
    _thermal_conductivity_constants = [0.23638, -0.00024263,0,0,0]
    _vapor_pressure_constants = [100.95, -8873.20, -11.451, 6.13e-6,2]
    _enthalpy_constants = [6.352, 0.3986,0,0,0]
