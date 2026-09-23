from .base import Component
from processpi.units import *

class _2Hexanone(Component):
    """
    Represents the properties and constants for 2Hexanone(C6?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Hexanone, which are essential for various process engineering calculations.
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
    name = "2Hexanone"
    formula = "C6?H12?O"
    molecular_weight = 100.159

    # Critical properties
    _critical_temperature = Temperature(587.61, "K")
    _critical_pressure = Pressure(3.287, "MPa")
    _critical_volume = Volume(0.378, "m3")
    _critical_zc = 0.254
    _critical_acentric_factor = 0.3846

    _density_constants = [0.67816, 0.25634, 587.61, 0.28365]
    _specific_heat_constants = [0.0, -107.47, 0.2062, 0.00070293, 0.0, 2.0185, 2.7087]
    _viscosity_constants = [-11.445, 1187.2, 0.0029076]
    _thermal_conductivity_constants = [0.21076, -0.00024]
    _vapor_pressure_constants = [107.44, 0.0, -12.679, 8.46e-06, 2.0]
    _enthalpy_constants = [5.6231, 0.38207]
