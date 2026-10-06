from .base import Component
from processpi.units import *

class _233Trimethylpentane(Component):
    """
    Represents the properties and constants for 233Trimethylpentane(C8?H18?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 233Trimethylpentane, which are essential for various process engineering calculations.
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
    name = "233Trimethylpentane"
    formula = "C8?H18?"
    molecular_weight = 114.229

    # Critical properties
    _critical_temperature = Temperature(573.5, "K")
    _critical_pressure = Pressure(2.82, "MPa")
    _critical_volume = Volume(0.455, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.2903

    _density_constants = [0.6028, 0.27446, 573.5, 0.2741]
    _specific_heat_constants = [0.0, 0.0, 3.2187, 0.0, 0.0, 2.3791, 2.5757]
    _viscosity_constants = [-4.0309, 990.76, -1.1771]
    _thermal_conductivity_constants = [0.16815, -0.00020535]
    _vapor_pressure_constants = [83.105, 0.0, -9.1858, 6.47e-06, 2.0]
    _enthalpy_constants = [4.991, 0.383]
