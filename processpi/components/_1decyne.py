from .base import Component
from processpi.units import *

class _1Decyne(Component):
    """
    Represents the properties and constants for 1Decyne(C10?H18?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Decyne, which are essential for various process engineering calculations.
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
    name = "1Decyne"
    formula = "C10?H18?"
    molecular_weight = 138.25

    # Critical properties
    _critical_temperature = Temperature(619.85, "K")
    _critical_pressure = Pressure(2.37, "MPa")
    _critical_volume = Volume(0.552, "m3")
    _critical_zc = 0.254
    _critical_acentric_factor = 0.5178

    _density_constants = [0.46877, 0.25875, 619.85, 0.29479]
    _specific_heat_constants = [0.0, -371.23, 1.5774, 0.0, 0.0, 2.7466, 4.2629]
    _viscosity_constants = [-2.3633, 791.93, -1.2272]
    _thermal_conductivity_constants = [0.20839, -0.00023622]
    _vapor_pressure_constants = [142.94, 0.0, -17.818, 1.1e-05, 2.0]
    _enthalpy_constants = [6.9461, 0.42109]
