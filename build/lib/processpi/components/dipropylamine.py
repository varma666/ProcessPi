from .base import Component
from processpi.units import *

class DipropylAmine(Component):
    """
    Represents the properties and constants for Dipropyl amine(C6?H15?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dipropyl amine, which are essential for various process engineering calculations.
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
    name = "Dipropyl amine"
    formula = "C6?H15?N"
    molecular_weight = 101.19

    # Critical properties
    _critical_temperature = Temperature(550.0, "K")
    _critical_pressure = Pressure(3.14, "MPa")
    _critical_volume = Volume(0.402, "m3")
    _critical_zc = 0.276
    _critical_acentric_factor = 0.4497

    _density_constants = [0.659, 0.26428, 550.0, 0.2766]
    _specific_heat_constants = [0.0, 562.24, 0.0, 0.0, 0.0, 2.0537, 2.7846]
    _viscosity_constants = [-15.404, 1390.0, 0.5564]
    _thermal_conductivity_constants = [0.2224, -0.000314]
    _vapor_pressure_constants = [54.0, 0.0, -4.4981, 9.97e-18, 6.0]
    _enthalpy_constants = [5.428, 0.3665]
