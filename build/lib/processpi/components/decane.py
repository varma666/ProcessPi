from .base import Component
from processpi.units import *

class Decane(Component):
    """
    Represents the properties and constants for Decane(C10?H22?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Decane, which are essential for various process engineering calculations.
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
    name = "Decane"
    formula = "C10?H22?"
    molecular_weight = 142.282

    # Critical properties
    _critical_temperature = Temperature(617.7, "K")
    _critical_pressure = Pressure(2.11, "MPa")
    _critical_volume = Volume(0.617, "m3")
    _critical_zc = 0.254
    _critical_acentric_factor = 0.4923

    _density_constants = [0.41084, 0.25175, 617.7, 0.28571]
    _specific_heat_constants = [0.0, -197.91, 1.0737, 0.0, 0.0, 2.9409, 4.1478]
    _viscosity_constants = [-9.6489, 1181.1, -0.24367, 9.05e+34, -15.0]
    _thermal_conductivity_constants = [0.2063, -0.00025]
    _vapor_pressure_constants = [112.73, 0.0, -13.245, 7.13e-06, 2.0]
    _enthalpy_constants = [6.6126, 0.39797]
