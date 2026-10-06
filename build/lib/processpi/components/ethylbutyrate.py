from .base import Component
from processpi.units import *

class EthylButyrate(Component):
    """
    Represents the properties and constants for Ethyl butyrate(C6?H12?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethyl butyrate, which are essential for various process engineering calculations.
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
    name = "Ethyl butyrate"
    formula = "C6?H12?O2?"
    molecular_weight = 116.158

    # Critical properties
    _critical_temperature = Temperature(571.0, "K")
    _critical_pressure = Pressure(2.95, "MPa")
    _critical_volume = Volume(0.403, "m3")
    _critical_zc = 0.25
    _critical_acentric_factor = 0.4011

    _density_constants = [0.63566, 0.25613, 571.0, 0.27829]
    _specific_heat_constants = [0.0, 422.45, 0.20992, 0.0, 0.0, 2.2015, 3.0185]
    _viscosity_constants = [-15.485, 1325.6, 0.6432]
    _thermal_conductivity_constants = [0.21043, -0.00024903]
    _vapor_pressure_constants = [57.661, 0.0, -5.032, 8.25e-18, 6.0]
    _enthalpy_constants = [5.6419, 0.37985]
