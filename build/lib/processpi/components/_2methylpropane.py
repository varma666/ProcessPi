from .base import Component
from processpi.units import *

class _2Methylpropane(Component):
    """
    Represents the properties and constants for 2Methylpropane(C4?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Methylpropane, which are essential for various process engineering calculations.
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
    name = "2Methylpropane"
    formula = "C4?H10?"
    molecular_weight = 58.122

    # Critical properties
    _critical_temperature = Temperature(407.8, "K")
    _critical_pressure = Pressure(3.64, "MPa")
    _critical_volume = Volume(0.259, "m3")
    _critical_zc = 0.278
    _critical_acentric_factor = 0.1835

    _density_constants = [1.0631, 0.27506, 407.8, 0.2758]
    _specific_heat_constants = [0.0, 0.0, 14.759, -0.047909, 5.805e-05, 0.9961, 2.0725]
    _viscosity_constants = [-13.912, 797.09, 0.45308]
    _thermal_conductivity_constants = [0.20455, -0.00036589]
    _vapor_pressure_constants = [108.43, 0.0, -15.012, 0.0227, 1.0]
    _enthalpy_constants = [3.188, 0.39006]
