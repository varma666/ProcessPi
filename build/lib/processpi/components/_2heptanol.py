from .base import Component
from processpi.units import *

class _2Heptanol(Component):
    """
    Represents the properties and constants for 2Heptanol(C7?H16?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Heptanol, which are essential for various process engineering calculations.
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
    name = "2Heptanol"
    formula = "C7?H16?O"
    molecular_weight = 116.201

    # Critical properties
    _critical_temperature = Temperature(608.3, "K")
    _critical_pressure = Pressure(3.001, "MPa")
    _critical_volume = Volume(0.447, "m3")
    _critical_zc = 0.265
    _critical_acentric_factor = 0.5628

    _density_constants = [0.57114, 0.25534, 608.3, 0.26487]
    _specific_heat_constants = [0.0, 0.0, 3.44064, 0.0, 0.0, 2.2649, 4.7873]
    _viscosity_constants = [11.225, 25.319, -3.2694, 101000000000.0, -4.3444]
    _thermal_conductivity_constants = [0.21134, -0.00024776]
    _vapor_pressure_constants = [124.23, 0.0, -14.148, 6.95e-17, 5.7]
    _enthalpy_constants = [9.6433, 0.783, -0.27273, 0.038495]
