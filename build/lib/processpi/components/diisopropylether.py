from .base import Component
from processpi.units import *

class DiisopropylEther(Component):
    """
    Represents the properties and constants for Diisopropyl ether(C6?H14?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Diisopropyl ether, which are essential for various process engineering calculations.
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
    name = "Diisopropyl ether"
    formula = "C6?H14?O"
    molecular_weight = 102.175

    # Critical properties
    _critical_temperature = Temperature(500.05, "K")
    _critical_pressure = Pressure(2.88, "MPa")
    _critical_volume = Volume(0.386, "m3")
    _critical_zc = 0.267
    _critical_acentric_factor = 0.3387

    _density_constants = [0.69213, 0.26974, 500.05, 0.28571]
    _specific_heat_constants = [0.0, -4.5, 0.62, 0.0, 0.0, 1.8399, 2.3375]
    _viscosity_constants = [-11.5, 993.0, 0.022]
    _thermal_conductivity_constants = [0.19162, -0.0002762]
    _vapor_pressure_constants = [41.631, 0.0, -2.8551, 0.000637, 1.0]
    _enthalpy_constants = [4.6117, 0.4]
