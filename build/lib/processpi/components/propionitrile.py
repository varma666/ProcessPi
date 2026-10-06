from .base import Component
from processpi.units import *

class Propionitrile(Component):
    """
    Represents the properties and constants for Propionitrile(C3?H5?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Propionitrile, which are essential for various process engineering calculations.
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
    name = "Propionitrile"
    formula = "C3?H5?N"
    molecular_weight = 55.079

    # Critical properties
    _critical_temperature = Temperature(564.4, "K")
    _critical_pressure = Pressure(4.18, "MPa")
    _critical_volume = Volume(0.229, "m3")
    _critical_zc = 0.204
    _critical_acentric_factor = 0.3243

    _density_constants = [1.0224, 0.23452, 564.4, 0.2804]
    _specific_heat_constants = [0.0, -120.98, 0.42075, 0.0, 0.0, 1.1005, 1.3112]
    _viscosity_constants = [-5.7136, 703.62, -0.78123]
    _thermal_conductivity_constants = [0.26626, -0.0003307]
    _vapor_pressure_constants = [82.699, 0.0, -9.1506, 7.54e-06, 2.0]
    _enthalpy_constants = [4.9348, 0.41873]
