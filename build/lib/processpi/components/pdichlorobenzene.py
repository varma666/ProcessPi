from .base import Component
from processpi.units import *

class Pdichlorobenzene(Component):
    """
    Represents the properties and constants for pDichlorobenzene(C6?H4?Cl2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for pDichlorobenzene, which are essential for various process engineering calculations.
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
    name = "pDichlorobenzene"
    formula = "C6?H4?Cl2?"
    molecular_weight = 147.002

    # Critical properties
    _critical_temperature = Temperature(684.75, "K")
    _critical_pressure = Pressure(4.07, "MPa")
    _critical_volume = Volume(0.351, "m3")
    _critical_zc = 0.251
    _critical_acentric_factor = 0.2846

    _density_constants = [0.74858, 0.26276, 684.75, 0.30788]
    _specific_heat_constants = [0.0, -24.84, 0.48191, 0.0, 0.0, 1.7711, 2.4829]
    _viscosity_constants = [31.63, -1080.0, -6.114]
    _thermal_conductivity_constants = [0.16977, -0.0001799]
    _vapor_pressure_constants = [88.31, 0.0, -9.6308, 4.58e-06, 2.0]
    _enthalpy_constants = [5.9765, 0.38559]
