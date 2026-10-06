from .base import Component
from processpi.units import *

class Propylbenzene(Component):
    """
    Represents the properties and constants for Propylbenzene(C9?H12?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Propylbenzene, which are essential for various process engineering calculations.
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
    name = "Propylbenzene"
    formula = "C9?H12?"
    molecular_weight = 120.192

    # Critical properties
    _critical_temperature = Temperature(638.35, "K")
    _critical_pressure = Pressure(3.2, "MPa")
    _critical_volume = Volume(0.44, "m3")
    _critical_zc = 0.265
    _critical_acentric_factor = 0.3444

    _density_constants = [0.57233, 0.25171, 638.35, 0.29616]
    _specific_heat_constants = [0.0, -101.8, 0.79, 0.0, 0.0, 1.8051, 2.7806]
    _viscosity_constants = [-18.282, 1549.7, 1.0454]
    _thermal_conductivity_constants = [0.18707, -0.00019846]
    _vapor_pressure_constants = [91.379, 0.0, -10.176, 5.62e-06, 2.0]
    _enthalpy_constants = [5.8887, 0.38534]
