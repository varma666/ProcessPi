from .base import Component
from processpi.units import *

class Biphenyl(Component):
    """
    Represents the properties and constants for Biphenyl(C12?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Biphenyl, which are essential for various process engineering calculations.
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
    name = "Biphenyl"
    formula = "C12?H10?"
    molecular_weight = 154.208

    # Critical properties
    _critical_temperature = Temperature(773.0, "K")
    _critical_pressure = Pressure(3.38, "MPa")
    _critical_volume = Volume(0.497, "m3")
    _critical_zc = 0.261
    _critical_acentric_factor = 0.4029

    _density_constants = [0.52257, 0.25833, 773.0, 0.27026]
    _specific_heat_constants = [0.0, 429.3, 0.0, 0.0, 0.0, 2.6868, 3.5075]
    _viscosity_constants = [-9.9265, 1576.3, -0.21119]
    _thermal_conductivity_constants = [0.19053, -0.00015145]
    _vapor_pressure_constants = [77.314, 0.0, -7.5079, 2.24e-18, 6.0]
    _enthalpy_constants = [7.635, 0.39182]
