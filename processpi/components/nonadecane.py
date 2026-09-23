from .base import Component
from processpi.units import *

class Nonadecane(Component):
    """
    Represents the properties and constants for Nonadecane(C19?H40?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nonadecane, which are essential for various process engineering calculations.
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
    name = "Nonadecane"
    formula = "C19?H40?"
    molecular_weight = 268.521

    # Critical properties
    _critical_temperature = Temperature(758.0, "K")
    _critical_pressure = Pressure(1.21, "MPa")
    _critical_volume = Volume(1.26, "m3")
    _critical_zc = 0.242
    _critical_acentric_factor = 0.8522

    _density_constants = [0.19199, 0.23337, 758.0, 0.28571]
    _specific_heat_constants = [0.0, 762.08, 0.20481, 0.0, 0.0, 5.9409, 8.7663]
    _viscosity_constants = [-16.403, 2119.5, 0.6881]
    _thermal_conductivity_constants = [0.21229, -0.00022]
    _vapor_pressure_constants = [182.54, 0.0, -22.498, 7.4e-06, 2.0]
    _enthalpy_constants = [11.674, 0.45865]
