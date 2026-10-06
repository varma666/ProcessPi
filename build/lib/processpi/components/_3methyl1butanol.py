from .base import Component
from processpi.units import *

class _3Methyl1Butanol(Component):
    """
    Represents the properties and constants for 3Methyl1butanol(C5?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 3Methyl1butanol, which are essential for various process engineering calculations.
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
    name = "3Methyl1butanol"
    formula = "C5?H12?O"
    molecular_weight = 88.148

    # Critical properties
    _critical_temperature = Temperature(577.2, "K")
    _critical_pressure = Pressure(3.93, "MPa")
    _critical_volume = Volume(0.329, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.5939

    _density_constants = [0.80828, 0.26783, 577.2, 0.23588]
    _specific_heat_constants = [0.0, 0.0, 3.4223, 0.0, 0.0, 1.5254, 3.4411]
    _viscosity_constants = [-25.882, 3359.4, 1.5787]
    _thermal_conductivity_constants = [0.17471, -0.0001256]
    _vapor_pressure_constants = [121.85, 0.0, -13.869, 1.43e-17, 6.0]
    _enthalpy_constants = [10.178, 1.3211, -1.2234, 0.44836]
