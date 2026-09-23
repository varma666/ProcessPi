from .base import Component
from processpi.units import *

class Chloroethane(Component):
    """
    Represents the properties and constants for Chloroethane(C2?H5?Cl).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Chloroethane, which are essential for various process engineering calculations.
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
    name = "Chloroethane"
    formula = "C2?H5?Cl"
    molecular_weight = 64.514

    # Critical properties
    _critical_temperature = Temperature(460.35, "K")
    _critical_pressure = Pressure(5.27, "MPa")
    _critical_volume = Volume(0.2, "m3")
    _critical_zc = 0.275
    _critical_acentric_factor = 0.1902

    _density_constants = [1.3, 0.26019, 460.35, 0.27155]
    _specific_heat_constants = [0.0, -345.15, 0.915, 0.0, 0.0, 0.98, 1.1632]
    _viscosity_constants = [-10.216, 702.0, -0.072]
    _thermal_conductivity_constants = [0.2438, -0.000419]
    _vapor_pressure_constants = [65.988, 0.0, -6.8586, 7.94e-06, 2.0]
    _enthalpy_constants = [3.524, 0.3652]
