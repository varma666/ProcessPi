from .base import Component
from processpi.units import *

class OxalicAcid(Component):
    """
    Represents the properties and constants for Oxalic acid(C2?H2?O4?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Oxalic acid, which are essential for various process engineering calculations.
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
    name = "Oxalic acid"
    formula = "C2?H2?O4?"
    molecular_weight = 90.035

    # Critical properties
    _critical_temperature = Temperature(804.0, "K")
    _critical_pressure = Pressure(7.02, "MPa")
    _critical_volume = Volume(0.205, "m3")
    _critical_zc = 0.215
    _critical_acentric_factor = 0.9176

    _density_constants = [1.0501, 0.215, 804.0, 0.28571]
    _specific_heat_constants = [0.0, -381.36, 0.64623, 0.0, 0.0, 1.374, 1.8052]
    _viscosity_constants = []
    _thermal_conductivity_constants = [0.3074, -0.00028101]
    _vapor_pressure_constants = [122.04, 0.0, -12.986, 2.09e-18, 6.0]
    _enthalpy_constants = [11.473, 0.37238]
