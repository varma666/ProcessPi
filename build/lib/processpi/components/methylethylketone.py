from .base import Component
from processpi.units import *

class MethylethylKetone(Component):
    """
    Represents the properties and constants for Methylethyl ketone(C4?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylethyl ketone, which are essential for various process engineering calculations.
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
    name = "Methylethyl ketone"
    formula = "C4?H8?O"
    molecular_weight = 72.106

    # Critical properties
    _critical_temperature = Temperature(535.5, "K")
    _critical_pressure = Pressure(4.15, "MPa")
    _critical_volume = Volume(0.267, "m3")
    _critical_zc = 0.249
    _critical_acentric_factor = 0.3234

    _density_constants = [0.93767, 0.25035, 535.5, 0.29964]
    _specific_heat_constants = [0.0, 200.87, -0.9597, 0.0019533, 0.0, 1.4905, 1.7511]
    _viscosity_constants = [-1.0598, 520.68, -1.4961]
    _thermal_conductivity_constants = [0.2197, -0.0002505]
    _vapor_pressure_constants = [72.698, 0.0, -7.5779, 5.65e-06, 2.0]
    _enthalpy_constants = [4.622, 0.355]
