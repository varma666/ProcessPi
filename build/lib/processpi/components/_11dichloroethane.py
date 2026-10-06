from .base import Component
from processpi.units import *

class _11Dichloroethane(Component):
    """
    Represents the properties and constants for 11Dichloroethane(C2?H4?Cl2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 11Dichloroethane, which are essential for various process engineering calculations.
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
    name = "11Dichloroethane"
    formula = "C2?H4?Cl2?"
    molecular_weight = 98.959

    # Critical properties
    _critical_temperature = Temperature(523.0, "K")
    _critical_pressure = Pressure(5.07, "MPa")
    _critical_volume = Volume(0.24, "m3")
    _critical_zc = 0.28
    _critical_acentric_factor = 0.2339

    _density_constants = [1.1055, 0.26533, 523.0, 0.287]
    _specific_heat_constants = [0.0, -94.63, 0.32, 0.0, 0.0, 1.196, 1.3001]
    _viscosity_constants = [-8.991, 870.2, -0.2805]
    _thermal_conductivity_constants = [0.18881, -0.00026083]
    _vapor_pressure_constants = [66.611, 0.0, -6.7301, 5.36e-06, 2.0]
    _enthalpy_constants = [4.2117, 0.36927]
