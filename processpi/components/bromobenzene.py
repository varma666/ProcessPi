from .base import Component
from processpi.units import *

class Bromobenzene(Component):
    """
    Represents the properties and constants for Bromobenzene(C6?H5?Br).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Bromobenzene, which are essential for various process engineering calculations.
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
    name = "Bromobenzene"
    formula = "C6?H5?Br"
    molecular_weight = 157.008

    # Critical properties
    _critical_temperature = Temperature(670.15, "K")
    _critical_pressure = Pressure(4.519, "MPa")
    _critical_volume = Volume(0.324, "m3")
    _critical_zc = 0.263
    _critical_acentric_factor = 0.2506

    _density_constants = [0.8226, 0.26632, 670.15, 0.2821]
    _specific_heat_constants = [0.0, -9.45, 0.358, 0.0, 0.0, 1.496, 2.0467]
    _viscosity_constants = [-20.611, 1656.5, 1.4415]
    _thermal_conductivity_constants = [0.16983, -0.0001981]
    _vapor_pressure_constants = [63.749, 0.0, -5.879, 5.21e-18, 6.0]
    _enthalpy_constants = [5.552, 0.37694]
