from .base import Component
from processpi.units import *

class EthylpropylEther(Component):
    """
    Represents the properties and constants for Ethylpropyl ether(C5?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylpropyl ether, which are essential for various process engineering calculations.
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
    name = "Ethylpropyl ether"
    formula = "C5?H12?O"
    molecular_weight = 88.148

    # Critical properties
    _critical_temperature = Temperature(500.23, "K")
    _critical_pressure = Pressure(3.37, "MPa")
    _critical_volume = Volume(0.339, "m3")
    _critical_zc = 0.275
    _critical_acentric_factor = 0.3473

    _density_constants = [0.7908, 0.266, 500.23, 0.292]
    _specific_heat_constants = [0.0, 726.3, -2.6047, 0.0040957, 0.0, 1.6686, 2.0358]
    _viscosity_constants = [0.7109, 386.51, -1.7754]
    _thermal_conductivity_constants = [0.22717, -0.0003298]
    _vapor_pressure_constants = [86.898, 0.0, -9.5758, 5.96e-17, 6.0]
    _enthalpy_constants = [5.438, 0.60624]
