from .base import Component
from processpi.units import *

class Pcresol(Component):
    """
    Represents the properties and constants for pCresol(C7?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for pCresol, which are essential for various process engineering calculations.
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
    name = "pCresol"
    formula = "C7?H8?O"
    molecular_weight = 108.138

    # Critical properties
    _critical_temperature = Temperature(704.65, "K")
    _critical_pressure = Pressure(5.15, "MPa")
    _critical_volume = Volume(0.277, "m3")
    _critical_zc = 0.244
    _critical_acentric_factor = 0.5072

    _density_constants = [1.1503, 0.31861, 704.65, 0.30104]
    _specific_heat_constants = [0.0, 0.0, 4.9427, -0.0054367, 0.0, 2.274, 2.5794]
    _viscosity_constants = [-1.6355, 1052.9, -1.3891, 3.68e+17, -7.0]
    _thermal_conductivity_constants = [0.17971, -0.00012037]
    _vapor_pressure_constants = [118.53, 0.0, -13.293, 8.7e-18, 6.0]
    _enthalpy_constants = [8.4942, 0.50234]
