from .base import Component
from processpi.units import *

class IsopropylAmine(Component):
    """
    Represents the properties and constants for Isopropyl amine(C3?H9?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Isopropyl amine, which are essential for various process engineering calculations.
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
    name = "Isopropyl amine"
    formula = "C3?H9?N"
    molecular_weight = 59.11

    # Critical properties
    _critical_temperature = Temperature(471.85, "K")
    _critical_pressure = Pressure(4.54, "MPa")
    _critical_volume = Volume(0.221, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.2759

    _density_constants = [1.2801, 0.2828, 471.85, 0.2972]
    _specific_heat_constants = [0.0, 0.0, -7.0145, 0.0086913, 0.0, 1.4621, 1.6671]
    _viscosity_constants = [-31.157, 1926.0, 2.925]
    _thermal_conductivity_constants = [0.237, -0.000332]
    _vapor_pressure_constants = [136.66, 0.0, -18.934, 0.0223, 1.0]
    _enthalpy_constants = [4.4041, 0.43325]
