from .base import Component
from processpi.units import *

class Heptane(Component):
    """
    Represents the properties and constants for Heptane(C7?H16?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Heptane, which are essential for various process engineering calculations.
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
    name = "Heptane"
    formula = "C7?H16?"
    molecular_weight = 100.202

    # Critical properties
    _critical_temperature = Temperature(540.2, "K")
    _critical_pressure = Pressure(2.74, "MPa")
    _critical_volume = Volume(0.428, "m3")
    _critical_zc = 0.261
    _critical_acentric_factor = 0.3495

    _density_constants = [0.61259, 0.26211, 540.2, 0.28141]
    _specific_heat_constants = [61.26, 0.0, 0.0, 0.0, 0.0, 1.9989, 4.0657]
    _viscosity_constants = [-9.4622, 877.07, -0.23445, 1.4e+22, -10.0]
    _thermal_conductivity_constants = [0.215, -0.000303]
    _vapor_pressure_constants = [87.829, 0.0, -9.8802, 7.21e-06, 2.0]
    _enthalpy_constants = [5.0014, 0.38795]
