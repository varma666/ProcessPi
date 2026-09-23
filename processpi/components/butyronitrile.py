from .base import Component
from processpi.units import *

class Butyronitrile(Component):
    """
    Represents the properties and constants for Butyronitrile(C4?H7?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Butyronitrile, which are essential for various process engineering calculations.
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
    name = "Butyronitrile"
    formula = "C4?H7?N"
    molecular_weight = 69.105

    # Critical properties
    _critical_temperature = Temperature(582.25, "K")
    _critical_pressure = Pressure(3.79, "MPa")
    _critical_volume = Volume(0.278, "m3")
    _critical_zc = 0.218
    _critical_acentric_factor = 0.3714

    _density_constants = [0.87533, 0.24331, 582.25, 0.28586]
    _specific_heat_constants = [0.0, 174.0, 0.0, 0.0, 0.0, 1.3206, 1.7199]
    _viscosity_constants = [-10.136, 1006.4, -0.1337]
    _thermal_conductivity_constants = [0.2597, -0.00031]
    _vapor_pressure_constants = [66.32, 0.0, -6.3087, 1.35e-17, 6.0]
    _enthalpy_constants = [5.22, 0.165, 0.6692, -0.539]
