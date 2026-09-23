from .base import Component
from processpi.units import *

class MethylisopropylSulfide(Component):
    """
    Represents the properties and constants for Methylisopropyl sulfide(C4?H10?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylisopropyl sulfide, which are essential for various process engineering calculations.
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
    name = "Methylisopropyl sulfide"
    formula = "C4?H10?S"
    molecular_weight = 90.187

    # Critical properties
    _critical_temperature = Temperature(553.1, "K")
    _critical_pressure = Pressure(4.021, "MPa")
    _critical_volume = Volume(0.328, "m3")
    _critical_zc = 0.28718
    _critical_acentric_factor = 0.2461

    _density_constants = [0.78912, 0.25915, 553.1, 0.26512]
    _specific_heat_constants = [0.0, -661.97, 2.4216, -0.0021383, 0.0, 1.5808, 1.8641]
    _viscosity_constants = [-11.075, 990.72]
    _thermal_conductivity_constants = [0.20978, -0.00026468]
    _vapor_pressure_constants = [52.82, 0.0, -4.442, 9.51e-18, 6.0]
    _enthalpy_constants = [4.5052, 0.36493]
