from .base import Component
from processpi.units import *

class Fluoroethane(Component):
    """
    Represents the properties and constants for Fluoroethane(C2?H5?F).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Fluoroethane, which are essential for various process engineering calculations.
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
    name = "Fluoroethane"
    formula = "C2?H5?F"
    molecular_weight = 48.06

    # Critical properties
    _critical_temperature = Temperature(375.31, "K")
    _critical_pressure = Pressure(5.028, "MPa")
    _critical_volume = Volume(0.164, "m3")
    _critical_zc = 0.264
    _critical_acentric_factor = 0.22

    _density_constants = [1.6525, 0.27099, 375.31, 0.2442]
    _specific_heat_constants = [0.0, -118.56, 0.55459, 0.0, 0.0, 0.7994, 0.8915]
    _viscosity_constants = [-10.758, 558.81, -0.016459]
    _thermal_conductivity_constants = [0.2595, -0.0005008]
    _vapor_pressure_constants = [56.639, 0.0, -5.5801, 9.9e-06, 2.0]
    _enthalpy_constants = [2.7617, 0.32162]
