from .base import Component
from processpi.units import *

class Trans2Butene(Component):
    """
    Represents the properties and constants for trans2Butene(C4?H8?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for trans2Butene, which are essential for various process engineering calculations.
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
    name = "trans2Butene"
    formula = "C4?H8?"
    molecular_weight = 56.106

    # Critical properties
    _critical_temperature = Temperature(428.6, "K")
    _critical_pressure = Pressure(4.1, "MPa")
    _critical_volume = Volume(0.238, "m3")
    _critical_zc = 0.274
    _critical_acentric_factor = 0.2176

    _density_constants = [1.1448, 0.27154, 428.6, 0.28419]
    _specific_heat_constants = [0.0, -104.7, 0.5214, 0.0, 0.0, 1.0986, 1.2322]
    _viscosity_constants = [-10.335, 521.39, -0.013184]
    _thermal_conductivity_constants = [0.21153, -0.00035056]
    _vapor_pressure_constants = [71.704, 0.0, -7.9053, 1.13e-05, 2.0]
    _enthalpy_constants = [3.3191, 0.36968]
