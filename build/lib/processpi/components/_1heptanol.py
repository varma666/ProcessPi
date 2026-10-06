from .base import Component
from processpi.units import *

class _1Heptanol(Component):
    """
    Represents the properties and constants for 1Heptanol(C7?H16?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Heptanol, which are essential for various process engineering calculations.
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
    name = "1Heptanol"
    formula = "C7?H16?O"
    molecular_weight = 116.201

    # Critical properties
    _critical_temperature = Temperature(632.3, "K")
    _critical_pressure = Pressure(3.085, "MPa")
    _critical_volume = Volume(0.444, "m3")
    _critical_zc = 0.261
    _critical_acentric_factor = 0.5621

    _density_constants = [0.55687, 0.24725, 632.3, 0.31471]
    _specific_heat_constants = [0.0, 0.0, 110.03, -0.19172, 0.00011968, 2.359, 3.8766]
    _viscosity_constants = [-66.654, 5325.8, 7.66, -2.25e-28, 9.9041]
    _thermal_conductivity_constants = [0.2239, -0.000226]
    _vapor_pressure_constants = [147.41, 0.0, -17.353, 1.13e-17, 6.0]
    _enthalpy_constants = [7.0236, -1.3652, 3.987, -2.2545]
