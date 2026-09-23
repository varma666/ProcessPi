from .base import Component
from processpi.units import *

class Benzophenone(Component):
    """
    Represents the properties and constants for Benzophenone(C13?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Benzophenone, which are essential for various process engineering calculations.
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
    name = "Benzophenone"
    formula = "C13?H10?O"
    molecular_weight = 182.218

    # Critical properties
    _critical_temperature = Temperature(830.0, "K")
    _critical_pressure = Pressure(3.352, "MPa")
    _critical_volume = Volume(0.5677, "m3")
    _critical_zc = 0.276
    _critical_acentric_factor = 0.5019

    _density_constants = [0.43743, 0.24833, 830.0, 0.27555]
    _specific_heat_constants = [0.0, 454.49, 0.0, 0.0, 0.0, 3.0218, 4.47]
    _viscosity_constants = [13.354, -232.91, -3.2685, 1.75e+20, -8.052]
    _thermal_conductivity_constants = [0.25867, -0.00022516]
    _vapor_pressure_constants = [88.404, 0.0, -8.9014, 1.93e-18, 6.0]
    _enthalpy_constants = [10.523, 0.87091, -0.45568]
