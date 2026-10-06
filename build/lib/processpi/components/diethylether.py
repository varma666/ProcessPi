from .base import Component
from processpi.units import *

class DiethylEther(Component):
    """
    Represents the properties and constants for Diethyl ether(C4?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Diethyl ether, which are essential for various process engineering calculations.
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
    name = "Diethyl ether"
    formula = "C4?H10?O"
    molecular_weight = 74.122

    # Critical properties
    _critical_temperature = Temperature(466.7, "K")
    _critical_pressure = Pressure(3.64, "MPa")
    _critical_volume = Volume(0.28, "m3")
    _critical_zc = 0.263
    _critical_acentric_factor = 0.2811

    _density_constants = [0.9554, 0.26847, 466.7, 0.2814]
    _specific_heat_constants = [0.0, 0.0, -5.5, 0.008763, 0.0, 1.4698, 3.3202]
    _viscosity_constants = [10.197, -63.8, -3.226]
    _thermal_conductivity_constants = [0.2495, -0.000407]
    _vapor_pressure_constants = [136.9, 0.0, -19.254, 0.0245, 1.0]
    _enthalpy_constants = [4.06, 0.3868]
