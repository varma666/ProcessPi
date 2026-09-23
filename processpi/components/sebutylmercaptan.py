from .base import Component
from processpi.units import *

class SeButylmercaptan(Component):
    """
    Represents the properties and constants for se-Butylmercaptan(C4?H10?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for se-Butylmercaptan, which are essential for various process engineering calculations.
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
    name = "se-Butylmercaptan"
    formula = "C4?H10?S"
    molecular_weight = 90.187

    # Critical properties
    _critical_temperature = Temperature(554.0, "K")
    _critical_pressure = Pressure(4.06, "MPa")
    _critical_volume = Volume(0.307, "m3")
    _critical_zc = 0.271
    _critical_acentric_factor = 0.2506

    _density_constants = [0.89137, 0.27365, 554.0, 0.2953]
    _specific_heat_constants = [0.0, -491.54, 1.7219, -0.0012499, 0.0, 1.6003, 1.8844]
    _viscosity_constants = [-10.903, 932.82, 0.023034]
    _thermal_conductivity_constants = [0.2069, -0.0002568]
    _vapor_pressure_constants = [60.649, 0.0, -5.6113, 1.59e-17, 6.0]
    _enthalpy_constants = [4.6432, 0.399]
