from .base import Component
from processpi.units import *

class _12Difluoroethane(Component):
    """
    Represents the properties and constants for 12Difluoroethane(C2?H4?F2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 12Difluoroethane, which are essential for various process engineering calculations.
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
    name = "12Difluoroethane"
    formula = "C2?H4?F2?"
    molecular_weight = 66.05

    # Critical properties
    _critical_temperature = Temperature(445.0, "K")
    _critical_pressure = Pressure(4.34, "MPa")
    _critical_volume = Volume(0.195, "m3")
    _critical_zc = 0.229
    _critical_acentric_factor = 0.2224

    _density_constants = [1.173, 0.22856, 445.0, 0.28571]
    _specific_heat_constants = [0.0, 109.85, 0.0, 0.0, 0.0, 1.0619, 1.1374]
    _viscosity_constants = [-10.072, 710.48, -0.14677]
    _thermal_conductivity_constants = [0.23171, -0.00038503]
    _vapor_pressure_constants = [84.625, 0.0, -9.871, 1.31e-05, 2.0]
    _enthalpy_constants = [3.4552, 0.3499]
