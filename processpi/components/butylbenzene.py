from .base import Component
from processpi.units import *

class Butylbenzene(Component):
    """
    Represents the properties and constants for Butylbenzene(C10?H14?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Butylbenzene, which are essential for various process engineering calculations.
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
    name = "Butylbenzene"
    formula = "C10?H14?"
    molecular_weight = 134.218

    # Critical properties
    _critical_temperature = Temperature(660.5, "K")
    _critical_pressure = Pressure(2.89, "MPa")
    _critical_volume = Volume(0.497, "m3")
    _critical_zc = 0.262
    _critical_acentric_factor = 0.3941

    _density_constants = [0.50812, 0.25238, 660.5, 0.29373]
    _specific_heat_constants = [0.0, -13.912, 0.72897, 0.0, 0.0, 2.0492, 2.9354]
    _viscosity_constants = [-23.802, 1887.2, 1.8479]
    _thermal_conductivity_constants = [0.18707, -0.00020037]
    _vapor_pressure_constants = [101.22, 0.0, -11.538, 5.92e-06, 2.0]
    _enthalpy_constants = [6.3487, 0.38222]
