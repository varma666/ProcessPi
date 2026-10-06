from .base import Component
from processpi.units import *

class DecylMercaptan(Component):
    """
    Represents the properties and constants for Decyl mercaptan(C10?H22?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Decyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Decyl mercaptan"
    formula = "C10?H22?S"
    molecular_weight = 174.347

    # Critical properties
    _critical_temperature = Temperature(696.0, "K")
    _critical_pressure = Pressure(2.13, "MPa")
    _critical_volume = Volume(0.624, "m3")
    _critical_zc = 0.23
    _critical_acentric_factor = 0.5874

    _density_constants = [0.44289, 0.27636, 696.0, 0.27668]
    _specific_heat_constants = [0.0, -160.93, 0.95561, 0.0, 0.0, 3.333, 4.8297]
    _viscosity_constants = [-11.464, 1510.1, -0.012754]
    _thermal_conductivity_constants = [0.20134, -0.00020826]
    _vapor_pressure_constants = [91.91, 0.0, -9.5957, 5.7e-18, 6.0]
    _enthalpy_constants = [8.0617, 0.41045]
