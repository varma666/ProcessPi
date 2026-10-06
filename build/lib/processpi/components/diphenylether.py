from .base import Component
from processpi.units import *

class DiphenylEther(Component):
    """
    Represents the properties and constants for Diphenyl ether(C12?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Diphenyl ether, which are essential for various process engineering calculations.
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
    name = "Diphenyl ether"
    formula = "C12?H10?O"
    molecular_weight = 170.207

    # Critical properties
    _critical_temperature = Temperature(766.8, "K")
    _critical_pressure = Pressure(3.08, "MPa")
    _critical_volume = Volume(0.503, "m3")
    _critical_zc = 0.243
    _critical_acentric_factor = 0.4389

    _density_constants = [0.52133, 0.26218, 766.8, 0.31033]
    _specific_heat_constants = [0.0, 447.67, 0.0, 0.0, 0.0, 2.6847, 3.8933]
    _viscosity_constants = [-12.373, 2017.5]
    _thermal_conductivity_constants = [0.18686, -0.00014953]
    _vapor_pressure_constants = [59.969, 0.0, -5.1538, 2e-18, 6.0]
    _enthalpy_constants = [6.8243, 0.30877]
