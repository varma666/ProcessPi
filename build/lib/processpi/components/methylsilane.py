from .base import Component
from processpi.units import *

class Methylsilane(Component):
    """
    Represents the properties and constants for Methylsilane(CH6?Si).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylsilane, which are essential for various process engineering calculations.
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
    name = "Methylsilane"
    formula = "CH6?Si"
    molecular_weight = 46.144

    # Critical properties
    _critical_temperature = Temperature(352.5, "K")
    _critical_pressure = Pressure(4.7, "MPa")
    _critical_volume = Volume(0.205, "m3")
    _critical_zc = 0.329
    _critical_acentric_factor = 0.1314

    _density_constants = [1.3052, 0.26757, 352.5, 0.28799]
    _specific_heat_constants = [0.0, 0.0, 0.0, 0.0, 0.0, 1.1347, 1.1347]
    _viscosity_constants = []
    _thermal_conductivity_constants = [0.2774, -0.00054608]
    _vapor_pressure_constants = [37.205, 0.0, -2.5993, 6.05e-06, 2.0]
    _enthalpy_constants = [2.2656, 0.30269]
