from .base import Component
from processpi.units import *

class _123Trimethylbenzene(Component):
    """
    Represents the properties and constants for 123Trimethylbenzene(C9?H12?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 123Trimethylbenzene, which are essential for various process engineering calculations.
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
    name = "123Trimethylbenzene"
    formula = "C9?H12?"
    molecular_weight = 120.192

    # Critical properties
    _critical_temperature = Temperature(664.5, "K")
    _critical_pressure = Pressure(3.454, "MPa")
    _critical_volume = Volume(0.414, "m3")
    _critical_zc = 0.259
    _critical_acentric_factor = 0.3666

    _density_constants = [0.6531, 0.27002, 664.5, 0.26268]
    _specific_heat_constants = [0.0, 324.54, 0.0, 0.0, 0.0, 1.9987, 2.6526]
    _viscosity_constants = [-11.756, 1483.1, -0.040387]
    _thermal_conductivity_constants = [0.18854, -0.0001963]
    _vapor_pressure_constants = [78.341, 0.0, -8.1458, 3.9e-06, 2.0]
    _enthalpy_constants = [5.9996, 0.35578]
