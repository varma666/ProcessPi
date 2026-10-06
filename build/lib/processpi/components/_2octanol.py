from .base import Component
from processpi.units import *

class _2Octanol(Component):
    """
    Represents the properties and constants for 2Octanol(C8?H18?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Octanol, which are essential for various process engineering calculations.
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
    name = "2Octanol"
    formula = "C8?H18?O"
    molecular_weight = 130.228

    # Critical properties
    _critical_temperature = Temperature(629.8, "K")
    _critical_pressure = Pressure(2.749, "MPa")
    _critical_volume = Volume(0.512, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.5807

    _density_constants = [0.50726, 0.25972, 629.8, 0.22]
    _specific_heat_constants = [0.0, 0.0, 3.52943, 0.0, 0.0, 2.7338, 5.7113]
    _viscosity_constants = [16.792, 1353.6, -4.6357, 2.67e+31, -13.039]
    _thermal_conductivity_constants = [0.20955, -0.00023733]
    _vapor_pressure_constants = [133.41, 0.0, -15.369, 2.99e-41, 14.0]
    _enthalpy_constants = [7.6376, -0.7612, 2.7875, -1.6033]
