from .base import Component
from processpi.units import *

class IsobutyricAcid(Component):
    """
    Represents the properties and constants for Isobutyric acid(C4?H8?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Isobutyric acid, which are essential for various process engineering calculations.
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
    name = "Isobutyric acid"
    formula = "C4?H8?O2?"
    molecular_weight = 88.105

    # Critical properties
    _critical_temperature = Temperature(605.0, "K")
    _critical_pressure = Pressure(3.7, "MPa")
    _critical_volume = Volume(0.292, "m3")
    _critical_zc = 0.215
    _critical_acentric_factor = 0.6141

    _density_constants = [0.88575, 0.25736, 605.0, 0.26265]
    _specific_heat_constants = [0.0, -65.35, 0.82867, 0.0, 0.0, 1.7031, 2.5114]
    _viscosity_constants = [-11.497, 1365.7, 0.036966]
    _thermal_conductivity_constants = [0.21668, -0.0002556]
    _vapor_pressure_constants = [110.38, 0.0, -12.262, 1.43e-17, 6.0]
    _enthalpy_constants = [4.0385, 0.82698, -2.033, 1.4769]
