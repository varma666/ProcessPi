from .base import Component
from processpi.units import *

class MethylBenzoate(Component):
    """
    Represents the properties and constants for Methyl benzoate(C8?H8?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl benzoate, which are essential for various process engineering calculations.
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
    name = "Methyl benzoate"
    formula = "C8?H8?O2?"
    molecular_weight = 136.148

    # Critical properties
    _critical_temperature = Temperature(693.0, "K")
    _critical_pressure = Pressure(3.59, "MPa")
    _critical_volume = Volume(0.436, "m3")
    _critical_zc = 0.272
    _critical_acentric_factor = 0.4205

    _density_constants = [0.53382, 0.23274, 693.0, 0.28147]
    _specific_heat_constants = [0.0, 279.75, 0.0, 0.0, 0.0, 1.9857, 2.5785]
    _viscosity_constants = [-21.971, 2267.4, 1.4173]
    _thermal_conductivity_constants = [0.22142, -0.00022759]
    _vapor_pressure_constants = [84.828, 0.0, -8.7063, 6.17e-18, 6.0]
    _enthalpy_constants = [6.8504, 0.38852]
