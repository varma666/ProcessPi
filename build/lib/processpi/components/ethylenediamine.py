from .base import Component
from processpi.units import *

class Ethylenediamine(Component):
    """
    Represents the properties and constants for Ethylenediamine(C2?H8?N2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylenediamine, which are essential for various process engineering calculations.
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
    name = "Ethylenediamine"
    formula = "C2?H8?N2?"
    molecular_weight = 60.098

    # Critical properties
    _critical_temperature = Temperature(593.0, "K")
    _critical_pressure = Pressure(6.29, "MPa")
    _critical_volume = Volume(0.264, "m3")
    _critical_zc = 0.337
    _critical_acentric_factor = 0.4724

    _density_constants = [0.7842, 0.20702, 593.0, 0.20254]
    _specific_heat_constants = [0.0, -150.2, 0.37044, 0.0, 0.0, 1.7168, 1.8226]
    _viscosity_constants = [-53.908, 4030.8, 5.9704]
    _thermal_conductivity_constants = [0.36434, -0.0004433]
    _vapor_pressure_constants = [73.51, 0.0, -7.1435, 1.21e-17, 6.0]
    _enthalpy_constants = [5.7521, 0.34513]
