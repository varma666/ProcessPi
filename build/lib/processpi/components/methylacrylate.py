from .base import Component
from processpi.units import *

class MethylAcrylate(Component):
    """
    Represents the properties and constants for Methyl acrylate(C4?H6?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl acrylate, which are essential for various process engineering calculations.
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
    name = "Methyl acrylate"
    formula = "C4?H6?O2?"
    molecular_weight = 86.089

    # Critical properties
    _critical_temperature = Temperature(536.0, "K")
    _critical_pressure = Pressure(4.25, "MPa")
    _critical_volume = Volume(0.27, "m3")
    _critical_zc = 0.258
    _critical_acentric_factor = 0.3423

    _density_constants = [0.97286, 0.26267, 536.0, 0.2508]
    _specific_heat_constants = [0.0, 0.0, 2.568, 0.0, 0.0, 1.493, 1.9084]
    _viscosity_constants = [10.848, 75.0, -3.297]
    _thermal_conductivity_constants = [0.26082, -0.0003506]
    _vapor_pressure_constants = [107.69, 0.0, -13.916, 0.0152, 1.0]
    _enthalpy_constants = [4.68, 0.349]
