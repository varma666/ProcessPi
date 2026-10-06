from .base import Component
from processpi.units import *

class HeptanoicAcid(Component):
    """
    Represents the properties and constants for Heptanoic acid(C7?H14?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Heptanoic acid, which are essential for various process engineering calculations.
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
    name = "Heptanoic acid"
    formula = "C7?H14?O2?"
    molecular_weight = 130.185

    # Critical properties
    _critical_temperature = Temperature(677.3, "K")
    _critical_pressure = Pressure(3.043, "MPa")
    _critical_volume = Volume(0.466, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.7564

    _density_constants = [0.53066, 0.24729, 677.3, 0.28289]
    _specific_heat_constants = [0.0, -23.206, 0.88395, 0.0, 0.0, 2.5087, 4.0065]
    _viscosity_constants = [-40.543, 3328.3, 4.1804]
    _thermal_conductivity_constants = [0.202, -0.0002]
    _vapor_pressure_constants = [120.47, 0.0, -13.31, 5.84e-18, 6.0]
    _enthalpy_constants = [11.274, 0.86047, -0.40661, -0.012644]
