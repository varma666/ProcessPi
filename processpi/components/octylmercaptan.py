from .base import Component
from processpi.units import *

class OctylMercaptan(Component):
    """
    Represents the properties and constants for Octyl mercaptan(C8?H18?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Octyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Octyl mercaptan"
    formula = "C8?H18?S"
    molecular_weight = 146.294

    # Critical properties
    _critical_temperature = Temperature(667.3, "K")
    _critical_pressure = Pressure(2.52, "MPa")
    _critical_volume = Volume(0.518, "m3")
    _critical_zc = 0.235
    _critical_acentric_factor = 0.4497

    _density_constants = [0.52577, 0.27234, 667.3, 0.30063]
    _specific_heat_constants = [0.0, -33.198, 0.67889, 0.0, 0.0, 2.7118, 3.7573]
    _viscosity_constants = [-11.498, 1362.1, 0.015575]
    _thermal_conductivity_constants = [0.2012, -0.0002142]
    _vapor_pressure_constants = [78.368, 0.0, -7.8202, 5.66e-18, 6.0]
    _enthalpy_constants = [6.8907, 0.40017]
