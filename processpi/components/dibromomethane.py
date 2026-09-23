from .base import Component
from processpi.units import *

class Dibromomethane(Component):
    """
    Represents the properties and constants for Dibromomethane(CH2?Br2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dibromomethane, which are essential for various process engineering calculations.
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
    name = "Dibromomethane"
    formula = "CH2?Br2?"
    molecular_weight = 173.835

    # Critical properties
    _critical_temperature = Temperature(611.0, "K")
    _critical_pressure = Pressure(7.17, "MPa")
    _critical_volume = Volume(0.223, "m3")
    _critical_zc = 0.315
    _critical_acentric_factor = 0.2095

    _density_constants = [1.1136, 0.24834, 611.0, 0.27583]
    _specific_heat_constants = [0.0, -726.3, 1.3377, 0.0, 0.0, 1.0532, 1.1701]
    _viscosity_constants = [-10.013, 921.31]
    _thermal_conductivity_constants = [0.17558, -0.00022499]
    _vapor_pressure_constants = [86.295, 0.0, -9.5972, 6.78e-06, 2.0]
    _enthalpy_constants = [4.82, 0.3771]
