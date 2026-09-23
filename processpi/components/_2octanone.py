from .base import Component
from processpi.units import *

class _2Octanone(Component):
    """
    Represents the properties and constants for 2Octanone(C8?H16?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Octanone, which are essential for various process engineering calculations.
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
    name = "2Octanone"
    formula = "C8?H16?O"
    molecular_weight = 128.212

    # Critical properties
    _critical_temperature = Temperature(632.7, "K")
    _critical_pressure = Pressure(2.64, "MPa")
    _critical_volume = Volume(0.497, "m3")
    _critical_zc = 0.249
    _critical_acentric_factor = 0.4549

    _density_constants = [0.50006, 0.24851, 632.7, 0.29942]
    _specific_heat_constants = [0.0, -426.2, 1.1172, 0.0, 0.0, 2.6406, 3.666]
    _viscosity_constants = [-11.736, 1415.2, 0.0003618]
    _thermal_conductivity_constants = [0.2132, -0.0002494]
    _vapor_pressure_constants = [63.775, 0.0, -5.7359, 3.09e-18, 6.0]
    _enthalpy_constants = [6.5363, 0.38718]
