from .base import Component
from processpi.units import *

class Mdichlorobenzene(Component):
    """
    Represents the properties and constants for mDichlorobenzene(C6?H4?Cl2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for mDichlorobenzene, which are essential for various process engineering calculations.
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
    name = "mDichlorobenzene"
    formula = "C6?H4?Cl2?"
    molecular_weight = 147.002

    # Critical properties
    _critical_temperature = Temperature(683.95, "K")
    _critical_pressure = Pressure(4.07, "MPa")
    _critical_volume = Volume(0.351, "m3")
    _critical_zc = 0.251
    _critical_acentric_factor = 0.279

    _density_constants = [0.74495, 0.26147, 683.95, 0.31526]
    _specific_heat_constants = [0.0, 187.25, 0.0, 0.0, 0.0, 1.6139, 1.8978]
    _viscosity_constants = [-1.9265, 387.67, -1.1335, 150000000000000.0, -6.0]
    _thermal_conductivity_constants = [0.16694, -0.0001667]
    _vapor_pressure_constants = [53.187, 0.0, -4.3233, 2.31e-18, 6.0]
    _enthalpy_constants = [5.6899, 0.35765]
