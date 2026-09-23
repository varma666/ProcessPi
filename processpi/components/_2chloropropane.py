from .base import Component
from processpi.units import *

class _2Chloropropane(Component):
    """
    Represents the properties and constants for 2Chloropropane(C3?H7?Cl).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Chloropropane, which are essential for various process engineering calculations.
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
    name = "2Chloropropane"
    formula = "C3?H7?Cl"
    molecular_weight = 78.541

    # Critical properties
    _critical_temperature = Temperature(489.0, "K")
    _critical_pressure = Pressure(4.54, "MPa")
    _critical_volume = Volume(0.247, "m3")
    _critical_zc = 0.276
    _critical_acentric_factor = 0.1986

    _density_constants = [1.1202, 0.27669, 489.0, 0.27646]
    _specific_heat_constants = [0.0, 215.01, 0.0, 0.0, 0.0, 1.1236, 1.3577]
    _viscosity_constants = [-15.458, 1086.0, 0.654]
    _thermal_conductivity_constants = [0.21232, -0.0003149]
    _vapor_pressure_constants = [46.854, 0.0, -3.6533, 1.33e-17, 6.0]
    _enthalpy_constants = [3.8871, 0.38043]
