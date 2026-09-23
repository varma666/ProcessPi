from .base import Component
from processpi.units import *

class _12Dichloroethane(Component):
    """
    Represents the properties and constants for 12Dichloroethane(C2?H4?Cl2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 12Dichloroethane, which are essential for various process engineering calculations.
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
    name = "12Dichloroethane"
    formula = "C2?H4?Cl2?"
    molecular_weight = 98.959

    # Critical properties
    _critical_temperature = Temperature(561.6, "K")
    _critical_pressure = Pressure(5.37, "MPa")
    _critical_volume = Volume(0.22, "m3")
    _critical_zc = 0.253
    _critical_acentric_factor = 0.2866

    _density_constants = [1.2591, 0.27698, 561.6, 0.30492]
    _specific_heat_constants = [0.0, -444.74, 0.93009, 0.0, 0.0, 1.2601, 1.3885]
    _viscosity_constants = [15.312, -41.12, -3.919]
    _thermal_conductivity_constants = [0.214, -0.000266]
    _vapor_pressure_constants = [92.355, 0.0, -10.651, 9.14e-06, 2.0]
    _enthalpy_constants = [4.5507, 0.34444]
