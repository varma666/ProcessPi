from .base import Component
from processpi.units import *

class _224Trimethylpentane(Component):
    """
    Represents the properties and constants for 224Trimethylpentane(C8?H18?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 224Trimethylpentane, which are essential for various process engineering calculations.
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
    name = "224Trimethylpentane"
    formula = "C8?H18?"
    molecular_weight = 114.229

    # Critical properties
    _critical_temperature = Temperature(543.8, "K")
    _critical_pressure = Pressure(2.57, "MPa")
    _critical_volume = Volume(0.468, "m3")
    _critical_zc = 0.266
    _critical_acentric_factor = 0.3035

    _density_constants = [0.59059, 0.27424, 543.8, 0.2847]
    _specific_heat_constants = [0.0, 696.7, -1.3765, 0.0021734, 0.0, 1.8285, 3.9095]
    _viscosity_constants = [-12.928, 1137.5, 0.25725, -3.69e-28, 10.0]
    _thermal_conductivity_constants = [0.1659, -0.00022686]
    _vapor_pressure_constants = [84.912, 0.0, -9.5157, 7.22e-06, 2.0]
    _enthalpy_constants = [4.7711, 0.37949]
