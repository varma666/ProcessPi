from .base import Component
from processpi.units import *

class EthylMercaptan(Component):
    """
    Represents the properties and constants for Ethyl mercaptan(C2?H6?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Ethyl mercaptan"
    formula = "C2?H6?S"
    molecular_weight = 62.134

    # Critical properties
    _critical_temperature = Temperature(499.15, "K")
    _critical_pressure = Pressure(5.49, "MPa")
    _critical_volume = Volume(0.207, "m3")
    _critical_zc = 0.274
    _critical_acentric_factor = 0.1878

    _density_constants = [1.3047, 0.2694, 499.15, 0.27866]
    _specific_heat_constants = [0.0, -234.39, 0.59656, 0.0, 0.0, 1.1467, 1.2007]
    _viscosity_constants = [-9.7574, 729.43, -0.14912]
    _thermal_conductivity_constants = [0.23392, -0.0003206]
    _vapor_pressure_constants = [65.551, 0.0, -6.6853, 6.32e-06, 2.0]
    _enthalpy_constants = [3.844, 0.37534]
