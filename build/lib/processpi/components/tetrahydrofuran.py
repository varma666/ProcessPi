from .base import Component
from processpi.units import *

class Tetrahydrofuran(Component):
    """
    Represents the properties and constants for Tetrahydrofuran(C4?H8?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Tetrahydrofuran, which are essential for various process engineering calculations.
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
    name = "Tetrahydrofuran"
    formula = "C4?H8?O"
    molecular_weight = 72.106

    # Critical properties
    _critical_temperature = Temperature(540.15, "K")
    _critical_pressure = Pressure(5.19, "MPa")
    _critical_volume = Volume(0.224, "m3")
    _critical_zc = 0.259
    _critical_acentric_factor = 0.2254

    _density_constants = [1.2543, 0.28084, 540.15, 0.2912]
    _specific_heat_constants = [0.0, -800.47, 2.8934, -0.0025015, 0.0, 1.0721, 1.3546]
    _viscosity_constants = [-10.321, 900.92, -0.069128]
    _thermal_conductivity_constants = [0.19428, -0.000249]
    _vapor_pressure_constants = [54.898, 0.0, -4.7627, 1.43e-17, 6.0]
    _enthalpy_constants = [4.3021, 0.36972]
