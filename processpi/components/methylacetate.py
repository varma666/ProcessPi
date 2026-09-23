from .base import Component
from processpi.units import *

class MethylAcetate(Component):
    """
    Represents the properties and constants for Methyl acetate(C3?H6?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl acetate, which are essential for various process engineering calculations.
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
    name = "Methyl acetate"
    formula = "C3?H6?O2?"
    molecular_weight = 74.079

    # Critical properties
    _critical_temperature = Temperature(506.55, "K")
    _critical_pressure = Pressure(4.75, "MPa")
    _critical_volume = Volume(0.228, "m3")
    _critical_zc = 0.257
    _critical_acentric_factor = 0.3313

    _density_constants = [1.13, 0.2593, 506.55, 0.2764]
    _specific_heat_constants = [0.0, 270.9, 0.0, 0.0, 0.0, 1.2991, 1.6241]
    _viscosity_constants = [13.557, -187.3, -3.6592]
    _thermal_conductivity_constants = [0.2777, -0.000417]
    _vapor_pressure_constants = [61.267, 0.0, -5.6473, 2.11e-17, 6.0]
    _enthalpy_constants = [4.492, 0.3685]
