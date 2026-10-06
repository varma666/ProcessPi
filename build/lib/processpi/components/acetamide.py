from .base import Component
from processpi.units import *

class Acetamide(Component):
    """
    Represents the properties and constants for Acetamide(C2?H5?NO).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acetamide, which are essential for various process engineering calculations.
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
    name = "Acetamide"
    formula = "C2H5NO"
    molecular_weight = 59.067

    # Critical properties
    _critical_temperature = Temperature(761.0, "K")
    _critical_pressure = Pressure(6.6, "MPa")
    _critical_volume = Volume(0.215, "m3")
    _critical_zc = 0.224
    _critical_acentric_factor = 0.421

    _density_constants = [1.016, 0.21845, 761.0, 0.26116]
    _specific_heat_constants = [102300, 128.7,0,0,0]
    _viscosity_constants = [1.5525, 1376.4, -2.0126,0,0]
    _thermal_conductivity_constants = [0.39363, -0.00037053,0,0,0]
    _vapor_pressure_constants = [125.81, -12376, -14.589, 5.08e-06, 2.0]
    _enthalpy_constants = [8.107, 0.42,0,0,0]
