from .base import Component
from processpi.units import *

class _2Methyl2Propanol(Component):
    """
    Represents the properties and constants for 2Methyl2propanol(C4?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Methyl2propanol, which are essential for various process engineering calculations.
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
    name = "2Methyl2propanol"
    formula = "C4?H10?O"
    molecular_weight = 74.122

    # Critical properties
    _critical_temperature = Temperature(506.2, "K")
    _critical_pressure = Pressure(3.972, "MPa")
    _critical_volume = Volume(0.275, "m3")
    _critical_zc = 0.26
    _critical_acentric_factor = 0.6152

    _density_constants = [0.92128, 0.25442, 506.2, 0.27586]
    _specific_heat_constants = [0.0, 0.0, -17.661, 0.013617, 0.0, 2.2016, 2.9455]
    _viscosity_constants = [51.356, -1249.5, -9.4593, 3.69e+24, -9.8759]
    _thermal_conductivity_constants = [0.21258, -0.00029864]
    _vapor_pressure_constants = [172.27, 0.0, -22.113, 1.37e-05, 2.0]
    _enthalpy_constants = [7.7646, 0.56757]
