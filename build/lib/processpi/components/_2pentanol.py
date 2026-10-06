from .base import Component
from processpi.units import *

class _2Pentanol(Component):
    """
    Represents the properties and constants for 2Pentanol(C5?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Pentanol, which are essential for various process engineering calculations.
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
    name = "2Pentanol"
    formula = "C5?H12?O"
    molecular_weight = 88.148

    # Critical properties
    _critical_temperature = Temperature(561.0, "K")
    _critical_pressure = Pressure(3.7, "MPa")
    _critical_volume = Volume(0.326, "m3")
    _critical_zc = 0.259
    _critical_acentric_factor = 0.5549

    _density_constants = [0.79324, 0.25806, 561.0, 0.28571]
    _specific_heat_constants = [0.0, 0.0, 3.26306, 0.0, 0.0, 1.7642, 7.0158]
    _viscosity_constants = [-410.49, 18371.0, 61.985, -0.0095612, 1.2201]
    _thermal_conductivity_constants = [0.21875, -0.00027849]
    _vapor_pressure_constants = [122.26, 0.0, -13.943, 1.07e-42, 15.0]
    _enthalpy_constants = [11.111, 1.8011, -2.1801, 1.0641]
