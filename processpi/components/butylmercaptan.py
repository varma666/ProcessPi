from .base import Component
from processpi.units import *

class ButylMercaptan(Component):
    """
    Represents the properties and constants for Butyl mercaptan(C4?H10?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Butyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Butyl mercaptan"
    formula = "C4?H10?S"
    molecular_weight = 90.187

    # Critical properties
    _critical_temperature = Temperature(570.1, "K")
    _critical_pressure = Pressure(3.97, "MPa")
    _critical_volume = Volume(0.307, "m3")
    _critical_zc = 0.257
    _critical_acentric_factor = 0.2714

    _density_constants = [0.89458, 0.27463, 570.1, 0.28512]
    _specific_heat_constants = [0.0, -804.35, 2.7063, -0.0023017, 0.0, 1.6365, 1.9359]
    _viscosity_constants = [-10.807, 966.74, -0.014851]
    _thermal_conductivity_constants = [0.21143, -0.000258]
    _vapor_pressure_constants = [65.382, 0.0, -6.2585, 1.49e-17, 6.0]
    _enthalpy_constants = [4.9702, 0.41199]
