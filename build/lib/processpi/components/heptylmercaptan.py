from .base import Component
from processpi.units import *

class HeptylMercaptan(Component):
    """
    Represents the properties and constants for Heptyl mercaptan(C7?H16?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Heptyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Heptyl mercaptan"
    formula = "C7?H16?S"
    molecular_weight = 132.267

    # Critical properties
    _critical_temperature = Temperature(645.0, "K")
    _critical_pressure = Pressure(2.77, "MPa")
    _critical_volume = Volume(0.465, "m3")
    _critical_zc = 0.24
    _critical_acentric_factor = 0.4226

    _density_constants = [0.58622, 0.2726, 645.0, 0.29644]
    _specific_heat_constants = [0.0, -158.01, 0.78982, 0.0, 0.0, 2.4229, 3.3131]
    _viscosity_constants = [-11.812, 1291.9, 0.076469]
    _thermal_conductivity_constants = [0.2037, -0.0002252]
    _vapor_pressure_constants = [79.858, 0.0, -8.1043, 8.15e-18, 6.0]
    _enthalpy_constants = [6.5473, 0.40968]
