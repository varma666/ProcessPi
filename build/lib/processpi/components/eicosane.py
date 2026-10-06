from .base import Component
from processpi.units import *

class Eicosane(Component):
    """
    Represents the properties and constants for Eicosane(C20?H42?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Eicosane, which are essential for various process engineering calculations.
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
    name = "Eicosane"
    formula = "C20?H42?"
    molecular_weight = 282.547

    # Critical properties
    _critical_temperature = Temperature(768.0, "K")
    _critical_pressure = Pressure(1.16, "MPa")
    _critical_volume = Volume(1.34, "m3")
    _critical_zc = 0.243
    _critical_acentric_factor = 0.9069

    _density_constants = [0.18166, 0.23351, 768.0, 0.28571]
    _specific_heat_constants = [0.0, 807.32, 0.2122, 0.0, 0.0, 6.2299, 9.3154]
    _viscosity_constants = [-18.315, 2283.5, 0.95485]
    _thermal_conductivity_constants = [0.2178, -0.0002233]
    _vapor_pressure_constants = [203.66, 0.0, -25.525, 8.84e-06, 2.0]
    _enthalpy_constants = [12.86, 0.50351, 0.32986, -0.42184]
