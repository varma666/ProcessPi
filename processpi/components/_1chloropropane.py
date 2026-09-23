from .base import Component
from processpi.units import *

class _1Chloropropane(Component):
    """
    Represents the properties and constants for 1Chloropropane(C3?H7?Cl).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Chloropropane, which are essential for various process engineering calculations.
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
    name = "1Chloropropane"
    formula = "C3?H7?Cl"
    molecular_weight = 78.541

    # Critical properties
    _critical_temperature = Temperature(503.15, "K")
    _critical_pressure = Pressure(4.58, "MPa")
    _critical_volume = Volume(0.247, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.2277

    _density_constants = [1.087, 0.26832, 503.15, 0.28055]
    _specific_heat_constants = [0.0, -153.27, 0.50836, 0.0, 0.0, 1.2073, 1.3523]
    _viscosity_constants = [-13.994, 949.4, 0.50223, -6.16e-17, 6.0]
    _thermal_conductivity_constants = [0.20143, -0.00028925]
    _vapor_pressure_constants = [79.24, 0.0, -8.789, 8.45e-06, 2.0]
    _enthalpy_constants = [3.989, 0.37956]
