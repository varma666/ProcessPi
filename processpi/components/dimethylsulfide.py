from .base import Component
from processpi.units import *

class DimethylSulfide(Component):
    """
    Represents the properties and constants for Dimethyl sulfide(C2?H6?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dimethyl sulfide, which are essential for various process engineering calculations.
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
    name = "Dimethyl sulfide"
    formula = "C2?H6?S"
    molecular_weight = 62.134

    # Critical properties
    _critical_temperature = Temperature(503.04, "K")
    _critical_pressure = Pressure(5.53, "MPa")
    _critical_volume = Volume(0.201, "m3")
    _critical_zc = 0.266
    _critical_acentric_factor = 0.1943

    _density_constants = [1.4029, 0.27991, 503.04, 0.2741]
    _specific_heat_constants = [0.0, -380.06, 1.2035, -0.00084787, 0.0, 1.1276, 1.1959]
    _viscosity_constants = [-17.641, 1067.5, 1.0317]
    _thermal_conductivity_constants = [0.23942, -0.0003311]
    _vapor_pressure_constants = [84.39, 0.0, -9.6454, 1.01e-05, 2.0]
    _enthalpy_constants = [3.9022, 0.37731]
