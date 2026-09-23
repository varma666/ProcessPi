from .base import Component
from processpi.units import *

class MethylisopropylKetone(Component):
    """
    Represents the properties and constants for Methylisopropyl ketone(C5?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylisopropyl ketone, which are essential for various process engineering calculations.
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
    name = "Methylisopropyl ketone"
    formula = "C5?H10?O"
    molecular_weight = 86.132

    # Critical properties
    _critical_temperature = Temperature(553.4, "K")
    _critical_pressure = Pressure(3.8, "MPa")
    _critical_volume = Volume(0.31, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.3208

    _density_constants = [0.86567, 0.26836, 553.4, 0.28364]
    _specific_heat_constants = [0.0, -331.04, 0.98445, 0.0, 0.0, 1.6348, 2.361]
    _viscosity_constants = [-11.272, 1048.9, 0.00030493]
    _thermal_conductivity_constants = [0.2332, -0.0003044]
    _vapor_pressure_constants = [45.242, 0.0, -3.2551, 3.04e-18, 6.0]
    _enthalpy_constants = [4.7075, 0.33601]
