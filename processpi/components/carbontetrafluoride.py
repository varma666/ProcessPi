from .base import Component
from processpi.units import *

class CarbonTetrafluoride(Component):
    """
    Represents the properties and constants for Carbon tetrafluoride(CF4?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Carbon tetrafluoride, which are essential for various process engineering calculations.
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
    name = "Carbon tetrafluoride"
    formula = "CF4?"
    molecular_weight = 88.004

    # Critical properties
    _critical_temperature = Temperature(227.51, "K")
    _critical_pressure = Pressure(3.745, "MPa")
    _critical_volume = Volume(0.143, "m3")
    _critical_zc = 0.283
    _critical_acentric_factor = 0.179

    _density_constants = [1.955, 0.27884, 227.51, 0.28571]
    _specific_heat_constants = [0.0, -500.6, 2.2851, 0.0, 0.0, 0.781, 0.8007]
    _viscosity_constants = [-9.9212, 300.5]
    _thermal_conductivity_constants = [0.20771, -0.00078883]
    _vapor_pressure_constants = [61.89, 0.0, -7.086, 3.47e-05, 2.0]
    _enthalpy_constants = [1.9311, 0.94983, -1.0615, 0.51894]
