from .base import Component
from processpi.units import *

class SiliconTetrafluoride(Component):
    """
    Represents the properties and constants for Silicon tetrafluoride(F4?Si).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Silicon tetrafluoride, which are essential for various process engineering calculations.
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
    name = "Silicon tetrafluoride"
    formula = "F4?Si"
    molecular_weight = 104.079

    # Critical properties
    _critical_temperature = Temperature(259.0, "K")
    _critical_pressure = Pressure(3.72, "MPa")
    _critical_volume = Volume(0.202, "m3")
    _critical_zc = 0.349
    _critical_acentric_factor = 0.3858

    _density_constants = [1.1945, 0.24128, 259.0, 0.16693]
    _specific_heat_constants = [0.0, 0.0, 19.203, 0.0, 0.0, 1.3, 2.0403]
    _viscosity_constants = []
    _thermal_conductivity_constants = []
    _vapor_pressure_constants = [272.85, 0.0, -40.089, 6.37e-15, 6.0]
    _enthalpy_constants = [2.4105, 0.37988]
