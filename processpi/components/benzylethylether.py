from .base import Component
from processpi.units import *

class BenzylEthylEther(Component):
    """
    Represents the properties and constants for Benzyl ethyl ether(C9?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Benzyl ethyl ether, which are essential for various process engineering calculations.
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
    name = "Benzyl ethyl ether"
    formula = "C9?H12?O"
    molecular_weight = 136.191

    # Critical properties
    _critical_temperature = Temperature(662.0, "K")
    _critical_pressure = Pressure(3.11, "MPa")
    _critical_volume = Volume(0.442, "m3")
    _critical_zc = 0.25
    _critical_acentric_factor = 0.4332

    _density_constants = [0.60917, 0.26925, 662.0, 0.2632]
    _specific_heat_constants = [0.0, 480.0, 0.0, 0.0, 0.0, 2.1981, 3.0741]
    _viscosity_constants = [-11.46, 1497.0, -0.043397]
    _thermal_conductivity_constants = [0.2029, -0.0002226]
    _vapor_pressure_constants = [68.541, 0.0, -6.5804, 2.43e-06, 2.0]
    _enthalpy_constants = [6.228, 0.3411]
