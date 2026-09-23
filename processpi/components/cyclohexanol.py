from .base import Component
from processpi.units import *

class Cyclohexanol(Component):
    """
    Represents the properties and constants for Cyclohexanol(C6?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Cyclohexanol, which are essential for various process engineering calculations.
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
    name = "Cyclohexanol"
    formula = "C6?H12?O"
    molecular_weight = 100.159

    # Critical properties
    _critical_temperature = Temperature(650.1, "K")
    _critical_pressure = Pressure(4.26, "MPa")
    _critical_volume = Volume(0.322, "m3")
    _critical_zc = 0.254
    _critical_acentric_factor = 0.369

    _density_constants = [0.8243, 0.26545, 650.1, 0.28495]
    _specific_heat_constants = [0.0, 853.0, 0.0, 0.0, 0.0, 2.13, 3.302]
    _viscosity_constants = [280.87, -31869.0, -38.837, 0.0, -2.002]
    _thermal_conductivity_constants = [0.1715, -0.0001255]
    _vapor_pressure_constants = [189.19, 0.0, -24.148, 1.07e-05, 2.0]
    _enthalpy_constants = [9.1791, 0.6382]
