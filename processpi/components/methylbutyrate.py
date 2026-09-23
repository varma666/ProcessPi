from .base import Component
from processpi.units import *

class MethylButyrate(Component):
    """
    Represents the properties and constants for Methyl butyrate(C5?H10?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl butyrate, which are essential for various process engineering calculations.
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
    name = "Methyl butyrate"
    formula = "C5?H10?O2?"
    molecular_weight = 102.132

    # Critical properties
    _critical_temperature = Temperature(554.5, "K")
    _critical_pressure = Pressure(3.473, "MPa")
    _critical_volume = Volume(0.34, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.3775

    _density_constants = [0.76983, 0.26173, 554.5, 0.26879]
    _specific_heat_constants = [0.0, 129.1, 0.62516, 0.0, 0.0, 1.8678, 2.6474]
    _viscosity_constants = [-12.206, 1141.7, 0.15014]
    _thermal_conductivity_constants = [0.21748, -0.00025913]
    _vapor_pressure_constants = [71.87, 0.0, -7.0944, 1.49e-17, 6.0]
    _enthalpy_constants = [5.3781, 0.39523]
