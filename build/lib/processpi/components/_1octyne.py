from .base import Component
from processpi.units import *

class _1Octyne(Component):
    """
    Represents the properties and constants for 1Octyne(C8?H14?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Octyne, which are essential for various process engineering calculations.
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
    name = "1Octyne"
    formula = "C8?H14?"
    molecular_weight = 110.197

    # Critical properties
    _critical_temperature = Temperature(574.0, "K")
    _critical_pressure = Pressure(2.88, "MPa")
    _critical_volume = Volume(0.442, "m3")
    _critical_zc = 0.267
    _critical_acentric_factor = 0.4233

    _density_constants = [0.58945, 0.26052, 574.0, 0.28532]
    _specific_heat_constants = [0.0, 886.67, -0.69315, 0.0, 0.0, 1.9225, 2.8619]
    _viscosity_constants = [-3.8552, 684.22, -1.0071]
    _thermal_conductivity_constants = [0.2095, -0.00025334]
    _vapor_pressure_constants = [64.612, 0.0, -6.0261, 1.1e-17, 6.0]
    _enthalpy_constants = [5.4046, 0.35299]
