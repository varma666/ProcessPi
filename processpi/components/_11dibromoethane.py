from .base import Component
from processpi.units import *

class _11Dibromoethane(Component):
    """
    Represents the properties and constants for 11Dibromoethane(C2?H4?Br2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 11Dibromoethane, which are essential for various process engineering calculations.
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
    name = "11Dibromoethane"
    formula = "C2?H4?Br2?"
    molecular_weight = 187.861

    # Critical properties
    _critical_temperature = Temperature(628.0, "K")
    _critical_pressure = Pressure(6.03, "MPa")
    _critical_volume = Volume(0.276, "m3")
    _critical_zc = 0.319
    _critical_acentric_factor = 0.125

    _density_constants = [0.95523, 0.26364, 628.0, 0.29825]
    _specific_heat_constants = [0.0, -231.8, 0.5946, 0.0, 0.0, 1.2695, 1.4743]
    _viscosity_constants = [-10.457, 1101.1, -0.0031354]
    _thermal_conductivity_constants = [0.1426, -0.00016402]
    _vapor_pressure_constants = [62.711, 0.0, -5.7669, 1.04e-06, 2.0]
    _enthalpy_constants = [5.712, 0.5255]
