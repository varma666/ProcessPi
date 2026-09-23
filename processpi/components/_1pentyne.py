from .base import Component
from processpi.units import *

class _1Pentyne(Component):
    """
    Represents the properties and constants for 1Pentyne(C5?H8?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Pentyne, which are essential for various process engineering calculations.
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
    name = "1Pentyne"
    formula = "C5?H8?"
    molecular_weight = 68.117

    # Critical properties
    _critical_temperature = Temperature(481.2, "K")
    _critical_pressure = Pressure(4.17, "MPa")
    _critical_volume = Volume(0.277, "m3")
    _critical_zc = 0.289
    _critical_acentric_factor = 0.2899

    _density_constants = [0.8491, 0.2352, 481.2, 0.353]
    _specific_heat_constants = [0.0, 256.6, 0.0, 0.0, 0.0, 1.3752, 1.666]
    _viscosity_constants = [-1.7273, 424.34, -1.342]
    _thermal_conductivity_constants = [0.22102, -0.000322]
    _vapor_pressure_constants = [82.805, 0.0, -9.4301, 1.08e-05, 2.0]
    _enthalpy_constants = [3.954, 0.3512]
