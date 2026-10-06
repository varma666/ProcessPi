from .base import Component
from processpi.units import *

class _3Methylcyclopentene(Component):
    """
    Represents the properties and constants for 3Methylcyclopentene(C6?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 3Methylcyclopentene, which are essential for various process engineering calculations.
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
    name = "3Methylcyclopentene"
    formula = "C6?H10?"
    molecular_weight = 82.144

    # Critical properties
    _critical_temperature = Temperature(526.0, "K")
    _critical_pressure = Pressure(4.13, "MPa")
    _critical_volume = Volume(0.303, "m3")
    _critical_zc = 0.286
    _critical_acentric_factor = 0.2296

    _density_constants = [0.9109, 0.276, 526.0, 0.26756]
    _specific_heat_constants = [0.0, 346.93, 0.0, 0.0, 0.0, 1.1584, 1.6374]
    _viscosity_constants = [-6.7424, 788.86, -0.69862]
    _thermal_conductivity_constants = [0.1994, -0.00026149]
    _vapor_pressure_constants = [52.601, 0.0, -4.4554, 1.33e-17, 6.0]
    _enthalpy_constants = [4.209, 0.36779]
