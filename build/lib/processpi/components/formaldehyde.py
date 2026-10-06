from .base import Component
from processpi.units import *

class Formaldehyde(Component):
    """
    Represents the properties and constants for Formaldehyde(CH2?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Formaldehyde, which are essential for various process engineering calculations.
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
    name = "Formaldehyde"
    formula = "CH2?O"
    molecular_weight = 30.026

    # Critical properties
    _critical_temperature = Temperature(408.0, "K")
    _critical_pressure = Pressure(6.59, "MPa")
    _critical_volume = Volume(0.115, "m3")
    _critical_zc = 0.223
    _critical_acentric_factor = 0.2818

    _density_constants = [1.9415, 0.22309, 408.0, 0.28571]
    _specific_heat_constants = [0.0, 28.3, 0.0, 0.0, 0.0, 0.6767, 0.6852]
    _viscosity_constants = [-11.24, 751.69, -0.024579]
    _thermal_conductivity_constants = [0.37329, -0.00065]
    _vapor_pressure_constants = [101.51, 0.0, -13.765, 0.022, 1.0]
    _enthalpy_constants = [3.076, 0.2954]
