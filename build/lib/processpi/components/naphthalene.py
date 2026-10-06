from .base import Component
from processpi.units import *

class Naphthalene(Component):
    """
    Represents the properties and constants for Naphthalene(C10?H8?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Naphthalene, which are essential for various process engineering calculations.
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
    name = "Naphthalene"
    formula = "C10?H8?"
    molecular_weight = 128.171

    # Critical properties
    _critical_temperature = Temperature(748.4, "K")
    _critical_pressure = Pressure(4.05, "MPa")
    _critical_volume = Volume(0.407, "m3")
    _critical_zc = 0.265
    _critical_acentric_factor = 0.302

    _density_constants = [0.6348, 0.25838, 748.4, 0.27727]
    _specific_heat_constants = [0.0, 527.5, 0.0, 0.0, 0.0, 2.1623, 2.8888]
    _viscosity_constants = [-19.308, 1822.5, 1.218]
    _thermal_conductivity_constants = [0.17096, -0.00010059]
    _vapor_pressure_constants = [62.964, 0.0, -5.6317, 2.27e-18, 6.0]
    _enthalpy_constants = [7.0911, 0.46468]
