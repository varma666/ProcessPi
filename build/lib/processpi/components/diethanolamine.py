from .base import Component
from processpi.units import *

class DiethanolAmine(Component):
    """
    Represents the properties and constants for Diethanol amine(C4?H11?NO2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Diethanol amine, which are essential for various process engineering calculations.
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
    name = "Diethanol amine"
    formula = "C4?H11?NO2?"
    molecular_weight = 105.136

    # Critical properties
    _critical_temperature = Temperature(736.6, "K")
    _critical_pressure = Pressure(4.27, "MPa")
    _critical_volume = Volume(0.349, "m3")
    _critical_zc = 0.243
    _critical_acentric_factor = 0.9529

    _density_constants = [0.68184, 0.23796, 736.6, 0.2062]
    _specific_heat_constants = [0.0, 286.0, 0.0, 0.0, 0.0, 2.7033, 3.3908]
    _viscosity_constants = [-375.21, 17177.0, 66.66, -3.6367, 0.5]
    _thermal_conductivity_constants = [0.0218, 0.0010315, -1.355e-06]
    _vapor_pressure_constants = [106.38, 0.0, -11.06, 3.26e-18, 6.0]
    _enthalpy_constants = [10.154, 0.3403]
