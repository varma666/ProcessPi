from .base import Component
from processpi.units import *

class Acrylonitrile(Component):
    """
    Represents the properties and constants for Acrylonitrile(C3?H3?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acrylonitrile, which are essential for various process engineering calculations.
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
    name = "Acrylonitrile"
    formula = "C3?H3?N"
    molecular_weight = 53.063

    # Critical properties
    _critical_temperature = Temperature(535.0, "K")
    _critical_pressure = Pressure(4.48, "MPa")
    _critical_volume = Volume(0.212, "m3")
    _critical_zc = 0.214
    _critical_acentric_factor = 0.3498

    _density_constants = [1.0816, 0.2293, 535.0, 0.28939]
    _specific_heat_constants = [0.0, -109.75, 0.35441, 0.0, 0.0, 1.0183, 1.2271]
    _viscosity_constants = [2.019, 239.7, -1.8975]
    _thermal_conductivity_constants = [0.28941, -0.00041691]
    _vapor_pressure_constants = [87.604, 0.0, -10.101, 1.09e-05, 2.0]
    _enthalpy_constants = [4.155, 0.2733]
