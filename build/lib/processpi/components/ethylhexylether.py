from .base import Component
from processpi.units import *

class EthylhexylEther(Component):
    """
    Represents the properties and constants for Ethylhexyl ether(C8?H18?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylhexyl ether, which are essential for various process engineering calculations.
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
    name = "Ethylhexyl ether"
    formula = "C8?H18?O"
    molecular_weight = 130.228

    # Critical properties
    _critical_temperature = Temperature(583.0, "K")
    _critical_pressure = Pressure(2.46, "MPa")
    _critical_volume = Volume(0.487, "m3")
    _critical_zc = 0.247
    _critical_acentric_factor = 0.4944

    _density_constants = [0.55729, 0.2714, 583.0, 0.29538]
    _specific_heat_constants = [0.0, 458.22, 0.0, 0.0, 0.0, 2.8266, 3.3719]
    _viscosity_constants = [-11.311, 1337.2, -0.02982]
    _thermal_conductivity_constants = [0.19356, -0.00024102]
    _vapor_pressure_constants = [77.523, 0.0, -7.7757, 1.01e-17, 6.0]
    _enthalpy_constants = [6.2786, 0.39513]
