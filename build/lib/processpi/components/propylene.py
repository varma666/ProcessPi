from .base import Component
from processpi.units import *

class Propylene(Component):
    """
    Represents the properties and constants for Propylene(C3?H6?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Propylene, which are essential for various process engineering calculations.
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
    name = "Propylene"
    formula = "C3?H6?"
    molecular_weight = 42.08

    # Critical properties
    _critical_temperature = Temperature(364.85, "K")
    _critical_pressure = Pressure(4.6, "MPa")
    _critical_volume = Volume(0.185, "m3")
    _critical_zc = 0.281
    _critical_acentric_factor = 0.1376

    _density_constants = [1.4403, 0.26852, 364.85, 0.28775]
    _specific_heat_constants = [0.0, -343.72, 1.0905, 0.0, 0.0, 0.9235, 0.9208]
    _viscosity_constants = [-92.082, 1907.3, 15.639, -0.043098, 1.0]
    _thermal_conductivity_constants = [0.24719, -0.00048824]
    _vapor_pressure_constants = [43.905, 0.0, -3.4425, 1e-16, 6.0]
    _enthalpy_constants = [2.5216, 0.33721, -0.18399, 0.22377]
