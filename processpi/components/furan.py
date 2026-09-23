from .base import Component
from processpi.units import *

class Furan(Component):
    """
    Represents the properties and constants for Furan(C4?H4?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Furan, which are essential for various process engineering calculations.
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
    name = "Furan"
    formula = "C4?H4?O"
    molecular_weight = 68.074

    # Critical properties
    _critical_temperature = Temperature(490.15, "K")
    _critical_pressure = Pressure(5.5, "MPa")
    _critical_volume = Volume(0.218, "m3")
    _critical_zc = 0.294
    _critical_acentric_factor = 0.2015

    _density_constants = [1.1339, 0.24741, 490.15, 0.2612]
    _specific_heat_constants = [0.0, -215.69, 0.72691, 0.0, 0.0, 0.9949, 1.1609]
    _viscosity_constants = [-10.923, 894.63, -0.00068418]
    _thermal_conductivity_constants = [0.2198, -0.00031405]
    _vapor_pressure_constants = [74.738, 0.0, -8.0636, 7.47e-06, 2.0]
    _enthalpy_constants = [4.005, 0.3995]
