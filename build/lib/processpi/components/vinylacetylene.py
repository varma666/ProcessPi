from .base import Component
from processpi.units import *

class VinylAcetylene(Component):
    """
    Represents the properties and constants for Vinyl acetylene(C4?H4?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Vinyl acetylene, which are essential for various process engineering calculations.
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
    name = "Vinyl acetylene"
    formula = "C4?H4?"
    molecular_weight = 52.075

    # Critical properties
    _critical_temperature = Temperature(454.0, "K")
    _critical_pressure = Pressure(4.86, "MPa")
    _critical_volume = Volume(0.205, "m3")
    _critical_zc = 0.264
    _critical_acentric_factor = 0.1069

    _density_constants = [1.2703, 0.26041, 454.0, 0.297]
    _specific_heat_constants = [0.0, 135.0, 0.0, 0.0, 0.0, 0.9572, 1.0628]
    _viscosity_constants = [-2.2333, 320.37, -1.2915]
    _thermal_conductivity_constants = [0.22838, -0.00035173]
    _vapor_pressure_constants = [55.682, 0.0, -5.0136, 1.97e-17, 6.0]
    _enthalpy_constants = [3.649, 0.4, 0.043]
