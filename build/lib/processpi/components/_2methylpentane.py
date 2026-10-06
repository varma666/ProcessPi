from .base import Component
from processpi.units import *

class _2Methylpentane(Component):
    """
    Represents the properties and constants for 2Methylpentane(C6?H14?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Methylpentane, which are essential for various process engineering calculations.
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
    name = "2Methylpentane"
    formula = "C6?H14?"
    molecular_weight = 86.175

    # Critical properties
    _critical_temperature = Temperature(497.7, "K")
    _critical_pressure = Pressure(3.04, "MPa")
    _critical_volume = Volume(0.368, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.2791

    _density_constants = [0.72701, 0.26754, 497.7, 0.28268]
    _specific_heat_constants = [0.0, -47.83, 0.739, 0.0, 0.0, 1.4706, 2.0842]
    _viscosity_constants = [-12.86, 946.91, 0.26191]
    _thermal_conductivity_constants = [0.19334, -0.00028038]
    _vapor_pressure_constants = [53.579, 0.0, -4.6404, 1.94e-17, 6.0]
    _enthalpy_constants = [4.2522, 0.3807]
