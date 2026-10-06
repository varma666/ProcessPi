from .base import Component
from processpi.units import *

class _1Hexene(Component):
    """
    Represents the properties and constants for 1Hexene(C6?H12?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Hexene, which are essential for various process engineering calculations.
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
    name = "1Hexene"
    formula = "C6?H12?"
    molecular_weight = 84.159

    # Critical properties
    _critical_temperature = Temperature(504.0, "K")
    _critical_pressure = Pressure(3.21, "MPa")
    _critical_volume = Volume(0.348, "m3")
    _critical_zc = 0.267
    _critical_acentric_factor = 0.2888

    _density_constants = [0.76925, 0.26809, 504.0, 0.28571]
    _specific_heat_constants = [0.0, -200.37, 0.8784, 0.0, 0.0, 1.5354, 1.9673]
    _viscosity_constants = [-10.36, 775.85, -0.082348]
    _thermal_conductivity_constants = [0.19112, -8.3519e-05, -5.14e-07]
    _vapor_pressure_constants = [51.024, 0.0, -4.2463, 1.68e-17, 6.0]
    _enthalpy_constants = [4.1429, 0.49118, -0.44821, 0.32105]
