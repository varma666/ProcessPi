from .base import Component
from processpi.units import *

class Methyldichlorosilane(Component):
    """
    Represents the properties and constants for Methyldichlorosilane(CH4?Cl2?Si).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyldichlorosilane, which are essential for various process engineering calculations.
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
    name = "Methyldichlorosilane"
    formula = "CH4?Cl2?Si"
    molecular_weight = 115.034

    # Critical properties
    _critical_temperature = Temperature(483.0, "K")
    _critical_pressure = Pressure(3.95, "MPa")
    _critical_volume = Volume(0.289, "m3")
    _critical_zc = 0.284
    _critical_acentric_factor = 0.2758

    _density_constants = [0.97608, 0.28209, 483.0, 0.22529]
    _specific_heat_constants = [0.0, 413.0, 0.0, 0.0, 0.0, 1.3028, 1.7158]
    _viscosity_constants = [-10.517, 745.32]
    _thermal_conductivity_constants = [0.21956, -0.00032153]
    _vapor_pressure_constants = [79.788, 0.0, -9.0702, 1.15e-05, 2.0]
    _enthalpy_constants = [3.6756, 0.31266]
