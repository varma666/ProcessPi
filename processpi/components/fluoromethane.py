from .base import Component
from processpi.units import *

class Fluoromethane(Component):
    """
    Represents the properties and constants for Fluoromethane(CH3?F).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Fluoromethane, which are essential for various process engineering calculations.
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
    name = "Fluoromethane"
    formula = "CH3?F"
    molecular_weight = 34.033

    # Critical properties
    _critical_temperature = Temperature(317.42, "K")
    _critical_pressure = Pressure(5.875, "MPa")
    _critical_volume = Volume(0.113, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.198

    _density_constants = [2.1854, 0.24725, 317.42, 0.27558]
    _specific_heat_constants = [0.0, -132.32, 0.53772, 0.0, 0.0, 0.6676, 0.7166]
    _viscosity_constants = [-10.501, 427.78, 0.0086309]
    _thermal_conductivity_constants = [0.445, -0.001023]
    _vapor_pressure_constants = [59.123, 0.0, -6.1845, 1.66e-05, 2.0]
    _enthalpy_constants = [2.4708, 0.37014]
