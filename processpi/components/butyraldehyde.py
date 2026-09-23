from .base import Component
from processpi.units import *

class Butyraldehyde(Component):
    """
    Represents the properties and constants for Butyraldehyde(C4?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Butyraldehyde, which are essential for various process engineering calculations.
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
    name = "Butyraldehyde"
    formula = "C4?H8?O"
    molecular_weight = 72.106

    # Critical properties
    _critical_temperature = Temperature(537.2, "K")
    _critical_pressure = Pressure(4.32, "MPa")
    _critical_volume = Volume(0.258, "m3")
    _critical_zc = 0.25
    _critical_acentric_factor = 0.2774

    _density_constants = [1.0361, 0.26731, 537.2, 0.28397]
    _specific_heat_constants = [0.0, 0.0, -7.1579, 0.012755, 0.0, 1.4741, 1.6459]
    _viscosity_constants = [-10.057, 903.73, -0.13186]
    _thermal_conductivity_constants = [0.21915, -0.00024846]
    _vapor_pressure_constants = [99.33, 0.0, -11.733, 1e-05, 2.0]
    _enthalpy_constants = [4.6403, 0.3849]
