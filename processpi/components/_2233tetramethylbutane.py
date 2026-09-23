from .base import Component
from processpi.units import *

class _2233Tetramethylbutane(Component):
    """
    Represents the properties and constants for 2233Tetramethylbutane(C8?H18?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2233Tetramethylbutane, which are essential for various process engineering calculations.
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
    name = "2233Tetramethylbutane"
    formula = "C8?H18?"
    molecular_weight = 114.229

    # Critical properties
    _critical_temperature = Temperature(568.0, "K")
    _critical_pressure = Pressure(2.87, "MPa")
    _critical_volume = Volume(0.461, "m3")
    _critical_zc = 0.28
    _critical_acentric_factor = 0.245

    _density_constants = [0.58988, 0.27201, 568.0, 0.27341]
    _specific_heat_constants = [0.0, 630.73, 0.0, 0.0, 0.0, 2.8011, 3.1202]
    _viscosity_constants = [5.5351, 632.38, -2.6576]
    _thermal_conductivity_constants = [0.17835, -0.00023704]
    _vapor_pressure_constants = [57.963, 0.0, -5.2048, 9.13e-18, 6.0]
    _enthalpy_constants = [4.9055, 0.40678]
