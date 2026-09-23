from .base import Component
from processpi.units import *

class Benzonitrile(Component):
    """
    Represents the properties and constants for Benzonitrile(C7?H5?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Benzonitrile, which are essential for various process engineering calculations.
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
    name = "Benzonitrile"
    formula = "C7?H5?N"
    molecular_weight = 103.121

    # Critical properties
    _critical_temperature = Temperature(699.35, "K")
    _critical_pressure = Pressure(4.215, "MPa")
    _critical_volume = Volume(0.3132, "m3")
    _critical_zc = 0.227
    _critical_acentric_factor = 0.3662

    _density_constants = [0.8552, 0.26785, 699.35, 0.30523]
    _specific_heat_constants = [0.0, 242.61, 0.0, 0.0, 0.0, 1.5656, 2.0599]
    _viscosity_constants = [-20.236, 1737.4, 1.3531]
    _thermal_conductivity_constants = [0.21284, -0.00021587]
    _vapor_pressure_constants = [138.5, 0.0, -17.085, 9.56e-06, 2.0]
    _enthalpy_constants = [6.8077, 0.63344, -0.27365]
