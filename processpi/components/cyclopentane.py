from .base import Component
from processpi.units import *

class Cyclopentane(Component):
    """
    Represents the properties and constants for Cyclopentane(C5?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Cyclopentane, which are essential for various process engineering calculations.
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
    name = "Cyclopentane"
    formula = "C5?H10?"
    molecular_weight = 70.133

    # Critical properties
    _critical_temperature = Temperature(511.7, "K")
    _critical_pressure = Pressure(4.51, "MPa")
    _critical_volume = Volume(0.26, "m3")
    _critical_zc = 0.276
    _critical_acentric_factor = 0.1949

    _density_constants = [1.0897, 0.28356, 511.7, 0.25142]
    _specific_heat_constants = [0.0, -403.8, 1.7344, -0.0010975, 0.0, 0.9956, 1.3584]
    _viscosity_constants = [-3.2612, 614.16, -1.156]
    _thermal_conductivity_constants = [0.2066, -0.0002696]
    _vapor_pressure_constants = [66.341, 0.0, -6.8103, 6.19e-06, 2.0]
    _enthalpy_constants = [3.8911, 0.36111]
