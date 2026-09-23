from .base import Component
from processpi.units import *

class Ocresol(Component):
    """
    Represents the properties and constants for oCresol(C7?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for oCresol, which are essential for various process engineering calculations.
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
    name = "oCresol"
    formula = "C7?H8?O"
    molecular_weight = 108.138

    # Critical properties
    _critical_temperature = Temperature(697.55, "K")
    _critical_pressure = Pressure(5.01, "MPa")
    _critical_volume = Volume(0.282, "m3")
    _critical_zc = 0.244
    _critical_acentric_factor = 0.4339

    _density_constants = [1.0861, 0.30624, 697.55, 0.30587]
    _specific_heat_constants = [0.0, 0.0, -8.0367, 0.007254, 0.0, 2.3297, 2.5243]
    _viscosity_constants = [-0.033937, 390.77, -1.4547, 5020000000000.0, -5.0]
    _thermal_conductivity_constants = [0.19186, -0.0001303]
    _vapor_pressure_constants = [210.88, 0.0, -29.483, 0.0252, 1.0]
    _enthalpy_constants = [7.1979, 0.40317]
