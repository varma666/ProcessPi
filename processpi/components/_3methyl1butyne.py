from .base import Component
from processpi.units import *

class _3Methyl1Butyne(Component):
    """
    Represents the properties and constants for 3Methyl1butyne(C5?H8?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 3Methyl1butyne, which are essential for various process engineering calculations.
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
    name = "3Methyl1butyne"
    formula = "C5?H8?"
    molecular_weight = 68.117

    # Critical properties
    _critical_temperature = Temperature(463.2, "K")
    _critical_pressure = Pressure(4.2, "MPa")
    _critical_volume = Volume(0.275, "m3")
    _critical_zc = 0.3
    _critical_acentric_factor = 0.3081

    _density_constants = [0.94575, 0.26008, 463.2, 0.30807]
    _specific_heat_constants = [0.0, 191.1, 0.0, 0.0, 0.0, 1.4342, 1.6243]
    _viscosity_constants = [-1.8842, 433.58, -1.3238]
    _thermal_conductivity_constants = [0.20348, -0.0003106]
    _vapor_pressure_constants = [69.459, 0.0, -7.1125, 7.93e-17, 6.0]
    _enthalpy_constants = [3.792, 0.3565]
