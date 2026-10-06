from .base import Component
from processpi.units import *

class Cyclohexene(Component):
    """
    Represents the properties and constants for Cyclohexene(C6H10).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Cyclohexene, which are essential for various process engineering calculations.
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
    name = "Cyclohexene"
    formula = "C6H10"
    molecular_weight = 82.144

    # Critical properties
    _critical_temperature = Temperature(560.4, "K")
    _critical_pressure = Pressure(4.35, "MPa")
    _critical_volume = Volume(0.291, "m3")
    _critical_zc = 0.272
    _critical_acentric_factor = 0.2123

    _density_constants = [0.92997, 0.27056, 560.4, 0.28943]
    _specific_heat_constants = [105850,-60,0.68,0,0]
    _viscosity_constants = [-11.641, 1154.3, 0.066511,0,0]
    _thermal_conductivity_constants = [0.20926, -0.00026037,0,0,0]
    _vapor_pressure_constants = [88.184, -6624.90, -10.059, 8.26e-06, 2.0]
    _enthalpy_constants = [4.4405e-7, 0.37479,0,0,0]
