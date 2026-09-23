from .base import Component
from processpi.units import *

class Argon(Component):
    """
    Represents the properties and constants for Argon(Ar).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Argon, which are essential for various process engineering calculations.
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
    name = "Argon"
    formula = "Ar"
    molecular_weight = 39.948

    # Critical properties
    _critical_temperature = Temperature(150.86, "K")
    _critical_pressure = Pressure(4.898, "MPa")
    _critical_volume = Volume(0.07459, "m3")
    _critical_zc = 0.291
    _critical_acentric_factor = 0.0

    _density_constants = [3.8469, 0.2881, 150.86, 0.29783]
    _specific_heat_constants = [0.0, 0.0, 11.043, 0.0, 0.0, 0.4523, 0.6708]
    _viscosity_constants = [-8.8685, 204.29, -0.38305, -1.29e-22, 10.0]
    _thermal_conductivity_constants = [0.1819, -0.0003176, -4.11e-06]
    _vapor_pressure_constants = [42.127, 0.0, -4.1425, 5.73e-05, 2.0]
    _enthalpy_constants = [0.87308, 0.3526]
