from .base import Component
from processpi.units import *

class Pentane(Component):
    """
    Represents the properties and constants for Pentane(C5?H12?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Pentane, which are essential for various process engineering calculations.
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
    name = "Pentane"
    formula = "C5?H12?"
    molecular_weight = 72.149

    # Critical properties
    _critical_temperature = Temperature(469.7, "K")
    _critical_pressure = Pressure(3.37, "MPa")
    _critical_volume = Volume(0.313, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.2515

    _density_constants = [0.84947, 0.26726, 469.7, 0.27789]
    _specific_heat_constants = [0.0, -270.5, 0.99537, 0.0, 0.0, 1.4076, 2.0498]
    _viscosity_constants = [-53.509, 1836.6, 7.1409, -1.9627e-05, 2.0]
    _thermal_conductivity_constants = [0.2537, -0.000576, 3.44e-07]
    _vapor_pressure_constants = [78.741, 0.0, -8.8253, 9.62e-06, 2.0]
    _enthalpy_constants = [3.9109, 0.38681]
