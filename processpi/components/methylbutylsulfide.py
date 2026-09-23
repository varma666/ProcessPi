from .base import Component
from processpi.units import *

class MethylbutylSulfide(Component):
    """
    Represents the properties and constants for Methylbutyl sulfide(C5?H12?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylbutyl sulfide, which are essential for various process engineering calculations.
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
    name = "Methylbutyl sulfide"
    formula = "C5?H12?S"
    molecular_weight = 104.214

    # Critical properties
    _critical_temperature = Temperature(593.0, "K")
    _critical_pressure = Pressure(3.47, "MPa")
    _critical_volume = Volume(0.36, "m3")
    _critical_zc = 0.253
    _critical_acentric_factor = 0.3229

    _density_constants = [0.75509, 0.27183, 593.0, 0.29127]
    _specific_heat_constants = [0.0, -220.35, 0.76096, 0.0, 0.0, 1.8315, 2.8394]
    _viscosity_constants = [-10.97, 1067.3, -0.017484]
    _thermal_conductivity_constants = [0.20698, -0.00024439]
    _vapor_pressure_constants = [96.344, 0.0, -11.058, 7.31e-06, 2.0]
    _enthalpy_constants = [5.3416, 0.3835]
