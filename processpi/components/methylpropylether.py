from .base import Component
from processpi.units import *

class MethylpropylEther(Component):
    """
    Represents the properties and constants for Methylpropyl ether(C4?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylpropyl ether, which are essential for various process engineering calculations.
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
    name = "Methylpropyl ether"
    formula = "C4?H10?O"
    molecular_weight = 74.122

    # Critical properties
    _critical_temperature = Temperature(476.25, "K")
    _critical_pressure = Pressure(3.801, "MPa")
    _critical_volume = Volume(0.276, "m3")
    _critical_zc = 0.265
    _critical_acentric_factor = 0.277

    _density_constants = [0.96145, 0.26536, 476.25, 0.30088]
    _specific_heat_constants = [0.0, -102.09, 0.58113, 0.0, 0.0, 1.4086, 1.6888]
    _viscosity_constants = [-10.705, 788.94, -0.048383]
    _thermal_conductivity_constants = [0.24817, -0.0003774]
    _vapor_pressure_constants = [67.942, 0.0, -6.8067, 4.78e-17, 6.0]
    _enthalpy_constants = [4.2719, 0.43175]
