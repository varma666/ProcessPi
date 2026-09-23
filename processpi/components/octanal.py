from .base import Component
from processpi.units import *

class Octanal(Component):
    """
    Represents the properties and constants for Octanal(C8?H16?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Octanal, which are essential for various process engineering calculations.
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
    name = "Octanal"
    formula = "C8?H16?O"
    molecular_weight = 128.212

    # Critical properties
    _critical_temperature = Temperature(638.9, "K")
    _critical_pressure = Pressure(2.96, "MPa")
    _critical_volume = Volume(0.488, "m3")
    _critical_zc = 0.272
    _critical_acentric_factor = 0.4636

    _density_constants = [0.53636, 0.26174, 638.9, 0.26348]
    _specific_heat_constants = [0.0, 463.61, 0.0, 0.0, 0.0, 2.447, 3.3795]
    _viscosity_constants = [-10.191, 1072.4, -0.030553]
    _thermal_conductivity_constants = [0.20143, -0.00021102]
    _vapor_pressure_constants = [83.601, 0.0, -8.5711, 7.94e-18, 6.0]
    _enthalpy_constants = [6.7735, 0.40607]
