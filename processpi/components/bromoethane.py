from .base import Component
from processpi.units import *

class Bromoethane(Component):
    """
    Represents the properties and constants for Bromoethane(C2?H5?Br).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Bromoethane, which are essential for various process engineering calculations.
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
    name = "Bromoethane"
    formula = "C2?H5?Br"
    molecular_weight = 108.965

    # Critical properties
    _critical_temperature = Temperature(503.8, "K")
    _critical_pressure = Pressure(6.23, "MPa")
    _critical_volume = Volume(0.215, "m3")
    _critical_zc = 0.32
    _critical_acentric_factor = 0.2548

    _density_constants = [1.1908, 0.25595, 503.8, 0.29152]
    _specific_heat_constants = [0.0, -109.12, 0.44032, 0.0, 0.0, 0.8818, 1.0453]
    _viscosity_constants = [-10.015, 823.43, -0.11122]
    _thermal_conductivity_constants = [0.1799, -0.000262]
    _vapor_pressure_constants = [62.217, 0.0, -5.9761, 4.72e-17, 6.0]
    _enthalpy_constants = [3.9004, 0.38012]
