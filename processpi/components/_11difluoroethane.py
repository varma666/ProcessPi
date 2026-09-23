from .base import Component
from processpi.units import *

class _11Difluoroethane(Component):
    """
    Represents the properties and constants for 11Difluoroethane(C2?H4?F2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 11Difluoroethane, which are essential for various process engineering calculations.
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
    name = "11Difluoroethane"
    formula = "C2?H4?F2?"
    molecular_weight = 66.05

    # Critical properties
    _critical_temperature = Temperature(386.44, "K")
    _critical_pressure = Pressure(4.52, "MPa")
    _critical_volume = Volume(0.179, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.2751

    _density_constants = [1.4345, 0.25774, 386.44, 0.28178]
    _specific_heat_constants = [67.155, 0.0, 310.21, -490.54, 0.0, 0.9915, 1.6874]
    _viscosity_constants = [10.501, -52.181, -3.3459]
    _thermal_conductivity_constants = [0.27019, -0.000661, 3.44e-07]
    _vapor_pressure_constants = [73.491, 0.0, -8.1851, 1.3e-05, 2.0]
    _enthalpy_constants = [3.2312, 0.37653]
