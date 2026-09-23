from .base import Component
from processpi.units import *

class Cyclopentene(Component):
    """
    Represents the properties and constants for Cyclopentene(C5?H8?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Cyclopentene, which are essential for various process engineering calculations.
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
    name = "Cyclopentene"
    formula = "C5?H8?"
    molecular_weight = 68.117

    # Critical properties
    _critical_temperature = Temperature(507.0, "K")
    _critical_pressure = Pressure(4.8, "MPa")
    _critical_volume = Volume(0.245, "m3")
    _critical_zc = 0.279
    _critical_acentric_factor = 0.1961

    _density_constants = [1.1035, 0.27035, 507.0, 0.28699]
    _specific_heat_constants = [0.0, -349.7, 1.143, 0.0, 0.0, 0.9888, 1.2953]
    _viscosity_constants = [-4.1508, 599.77, -1.0308]
    _thermal_conductivity_constants = [0.21776, -0.00027783]
    _vapor_pressure_constants = [67.952, 0.0, -7.0785, 6.82e-06, 2.0]
    _enthalpy_constants = [3.8107, 0.3543]
