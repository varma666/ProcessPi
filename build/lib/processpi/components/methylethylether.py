from .base import Component
from processpi.units import *

class MethylethylEther(Component):
    """
    Represents the properties and constants for Methylethyl ether(C3?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylethyl ether, which are essential for various process engineering calculations.
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
    name = "Methylethyl ether"
    formula = "C3?H8?O"
    molecular_weight = 60.095

    # Critical properties
    _critical_temperature = Temperature(437.8, "K")
    _critical_pressure = Pressure(4.4, "MPa")
    _critical_volume = Volume(0.221, "m3")
    _critical_zc = 0.267
    _critical_acentric_factor = 0.2314

    _density_constants = [1.2635, 0.27878, 437.8, 0.2744]
    _specific_heat_constants = [0.0, 199.08, -0.061547, 0.0, 0.0, 1.1566, 1.3638]
    _viscosity_constants = [-11.104, 627.18, 0.036581]
    _thermal_conductivity_constants = [0.27304, -0.0004518]
    _vapor_pressure_constants = [78.586, 0.0, -8.7501, 9.17e-06, 2.0]
    _enthalpy_constants = [3.53, 0.376]
