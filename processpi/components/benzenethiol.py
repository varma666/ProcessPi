from .base import Component
from processpi.units import *

class Benzenethiol(Component):
    """
    Represents the properties and constants for Benzenethiol(C6?H6?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Benzenethiol, which are essential for various process engineering calculations.
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
    name = "Benzenethiol"
    formula = "C6?H6?S"
    molecular_weight = 110.177

    # Critical properties
    _critical_temperature = Temperature(689.0, "K")
    _critical_pressure = Pressure(4.74, "MPa")
    _critical_volume = Volume(0.315, "m3")
    _critical_zc = 0.261
    _critical_acentric_factor = 0.2628

    _density_constants = [0.83573, 0.26326, 689.0, 0.30798]
    _specific_heat_constants = [0.0, 180.34, 0.0, 0.0, 0.0, 1.6636, 1.9954]
    _viscosity_constants = [-8.4562, 1024.4, -0.30635]
    _thermal_conductivity_constants = [0.20996, -0.0002146]
    _vapor_pressure_constants = [77.765, 0.0, -7.7404, 4.31e-18, 6.0]
    _enthalpy_constants = [6.225, 0.4412]
