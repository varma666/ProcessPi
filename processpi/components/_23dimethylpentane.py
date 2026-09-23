from .base import Component
from processpi.units import *

class _23Dimethylpentane(Component):
    """
    Represents the properties and constants for 23Dimethylpentane(C7?H16?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 23Dimethylpentane, which are essential for various process engineering calculations.
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
    name = "23Dimethylpentane"
    formula = "C7?H16?"
    molecular_weight = 100.202

    # Critical properties
    _critical_temperature = Temperature(537.3, "K")
    _critical_pressure = Pressure(2.91, "MPa")
    _critical_volume = Volume(0.393, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.2964

    _density_constants = [0.72352, 0.28629, 537.3, 0.27121]
    _specific_heat_constants = [0.0, 59.2, 0.604, 0.0, 0.0, 1.5664, 2.5613]
    _viscosity_constants = [-12.08, 1112.2, 0.09654]
    _thermal_conductivity_constants = [0.17964, -0.000246]
    _vapor_pressure_constants = [78.335, 0.0, -8.5105, 6.43e-06, 2.0]
    _enthalpy_constants = [4.6533, 0.37577]
