from .base import Component
from processpi.units import *

class _1Butyne(Component):
    """
    Represents the properties and constants for 1Butyne(C4?H6?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Butyne, which are essential for various process engineering calculations.
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
    name = "1Butyne"
    formula = "C4?H6?"
    molecular_weight = 54.09

    # Critical properties
    _critical_temperature = Temperature(440.0, "K")
    _critical_pressure = Pressure(4.6, "MPa")
    _critical_volume = Volume(0.208, "m3")
    _critical_zc = 0.262
    _critical_acentric_factor = 0.247

    _density_constants = [1.3409, 0.27892, 440.0, 0.29661]
    _specific_heat_constants = [0.0, -300.4, 1.0216, 0.0, 0.0, 1.1426, 1.3759]
    _viscosity_constants = [-3.4644, 334.5, -1.0811]
    _thermal_conductivity_constants = [0.22334, -0.0003515]
    _vapor_pressure_constants = [77.004, 0.0, -8.5665, 1.02e-05, 2.0]
    _enthalpy_constants = [3.6972, 0.39168]
