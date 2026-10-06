from .base import Component
from processpi.units import *

class Hydrogen(Component):
    """
    Represents the properties and constants for Hydrogen(H2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hydrogen, which are essential for various process engineering calculations.
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
    name = "Hydrogen"
    formula = "H2?"
    molecular_weight = 2.016

    # Critical properties
    _critical_temperature = Temperature(33.19, "K")
    _critical_pressure = Pressure(1.313, "MPa")
    _critical_volume = Volume(0.064147, "m3")
    _critical_zc = 0.305
    _critical_acentric_factor = -0.216

    _density_constants = [5.414, 0.34893, 33.19, 0.2706]
    _specific_heat_constants = [66.653, 0.0, -123.63, 478.27, 0.0, 0.1262, 1.3122]
    _viscosity_constants = [-11.661, 24.7, -0.261, -4.1e-16, 10.0]
    _thermal_conductivity_constants = [-0.0917, 0.017678, -0.000382, -3.33e-06, 1.03e-07]
    _vapor_pressure_constants = [12.69, -94.896, 1.1125, 0.000329, 2.0]
    _enthalpy_constants = [0.10127, 0.698, -1.817, 1.447]
