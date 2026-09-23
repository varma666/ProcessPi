from .base import Component
from processpi.units import *

class EthylisopropylEther(Component):
    """
    Represents the properties and constants for Ethylisopropyl ether(C5?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylisopropyl ether, which are essential for various process engineering calculations.
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
    name = "Ethylisopropyl ether"
    formula = "C5?H12?O"
    molecular_weight = 88.148

    # Critical properties
    _critical_temperature = Temperature(489.0, "K")
    _critical_pressure = Pressure(3.41, "MPa")
    _critical_volume = Volume(0.329, "m3")
    _critical_zc = 0.276
    _critical_acentric_factor = 0.3056

    _density_constants = [0.8185, 0.26929, 489.0, 0.30621]
    _specific_heat_constants = [0.0, 292.15, 0.0, 0.0, 0.0, 1.9335, 2.0153]
    _viscosity_constants = [-11.331, 908.46, 0.00042478]
    _thermal_conductivity_constants = [0.21928, -0.00032568]
    _vapor_pressure_constants = [57.723, 0.0, -5.2136, 2.3e-17, 6.0]
    _enthalpy_constants = [4.258, 0.37221]
