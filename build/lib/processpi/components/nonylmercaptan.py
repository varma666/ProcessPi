from .base import Component
from processpi.units import *

class NonylMercaptan(Component):
    """
    Represents the properties and constants for Nonyl mercaptan(C9?H20?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nonyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Nonyl mercaptan"
    formula = "C9?H20?S"
    molecular_weight = 160.32

    # Critical properties
    _critical_temperature = Temperature(681.0, "K")
    _critical_pressure = Pressure(2.31, "MPa")
    _critical_volume = Volume(0.571, "m3")
    _critical_zc = 0.233
    _critical_acentric_factor = 0.526

    _density_constants = [0.47377, 0.27052, 681.0, 0.30284]
    _specific_heat_constants = [0.0, -46.22, 0.79154, 0.0, 0.0, 3.0434, 4.3491]
    _viscosity_constants = [-11.319, 1428.0, -0.022545]
    _thermal_conductivity_constants = [0.20244, -0.00021343]
    _vapor_pressure_constants = [106.2, 0.0, -11.696, 8.9e-18, 6.0]
    _enthalpy_constants = [7.5239, 0.3991]
