from .base import Component
from processpi.units import *

class Cis2Butene(Component):
    """
    Represents the properties and constants for cis2Butene(C4?H8?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for cis2Butene, which are essential for various process engineering calculations.
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
    name = "cis2Butene"
    formula = "C4?H8?"
    molecular_weight = 56.106

    # Critical properties
    _critical_temperature = Temperature(435.5, "K")
    _critical_pressure = Pressure(4.21, "MPa")
    _critical_volume = Volume(0.234, "m3")
    _critical_zc = 0.272
    _critical_acentric_factor = 0.2019

    _density_constants = [1.1591, 0.27085, 435.5, 0.28116]
    _specific_heat_constants = [0.0, -65.47, -0.64, 0.002912, 0.0, 1.134, 1.5022]
    _viscosity_constants = [-10.346, 522.3, -0.011847]
    _thermal_conductivity_constants = [0.21378, -0.00035445]
    _vapor_pressure_constants = [72.541, 0.0, -7.9776, 1.04e-05, 2.0]
    _enthalpy_constants = [3.4358, 0.38004]
