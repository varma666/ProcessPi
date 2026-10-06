from .base import Component
from processpi.units import *

class Nonanal(Component):
    """
    Represents the properties and constants for Nonanal(C9?H18?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nonanal, which are essential for various process engineering calculations.
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
    name = "Nonanal"
    formula = "C9?H18?O"
    molecular_weight = 142.239

    # Critical properties
    _critical_temperature = Temperature(658.0, "K")
    _critical_pressure = Pressure(2.73, "MPa")
    _critical_volume = Volume(0.527, "m3")
    _critical_zc = 0.263
    _critical_acentric_factor = 0.5117

    _density_constants = [0.49587, 0.26135, 658.0, 0.30736]
    _specific_heat_constants = [0.0, 531.29, 0.0, 0.0, 0.0, 2.7238, 3.8554]
    _viscosity_constants = [-12.94, 1257.6, 0.37191]
    _thermal_conductivity_constants = [0.21523, -0.0002799, 9.57e-08]
    _vapor_pressure_constants = [337.71, 0.0, -50.224, 0.0473, 1.0]
    _enthalpy_constants = [7.3363, 0.41735]
