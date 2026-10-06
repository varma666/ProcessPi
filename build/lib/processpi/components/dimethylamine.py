from .base import Component
from processpi.units import *

class DimethylAmine(Component):
    """
    Represents the properties and constants for Dimethyl amine(C2?H7?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dimethyl amine, which are essential for various process engineering calculations.
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
    name = "Dimethyl amine"
    formula = "C2?H7?N"
    molecular_weight = 45.084

    # Critical properties
    _critical_temperature = Temperature(437.2, "K")
    _critical_pressure = Pressure(5.34, "MPa")
    _critical_volume = Volume(0.18, "m3")
    _critical_zc = 0.264
    _critical_acentric_factor = 0.2999

    _density_constants = [1.5436, 0.27784, 437.2, 0.2572]
    _specific_heat_constants = [0.0, 0.0, -13.781, 0.016924, 0.0, 1.1947, 1.3779]
    _viscosity_constants = [-10.93, 699.5]
    _thermal_conductivity_constants = [0.2454, -0.000338]
    _vapor_pressure_constants = [71.738, 0.0, -7.3324, 6.42e-17, 6.0]
    _enthalpy_constants = [4.09, 0.42005]
