from .base import Component
from processpi.units import *

class CyclohexylMercaptan(Component):
    """
    Represents the properties and constants for Cyclohexyl mercaptan(C6?H12?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Cyclohexyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Cyclohexyl mercaptan"
    formula = "C6?H12?S"
    molecular_weight = 116.224

    # Critical properties
    _critical_temperature = Temperature(664.0, "K")
    _critical_pressure = Pressure(3.97, "MPa")
    _critical_volume = Volume(0.355, "m3")
    _critical_zc = 0.255
    _critical_acentric_factor = 0.2641

    _density_constants = [0.78578, 0.27882, 664.0, 0.31067]
    _specific_heat_constants = [0.0, -179.12, 0.76723, 0.0, 0.0, 1.7118, 2.4334]
    _viscosity_constants = [-11.338, 1304.1, 9.2396e-05]
    _thermal_conductivity_constants = [0.18374, -0.0001925]
    _vapor_pressure_constants = [85.146, 0.0, -9.2982, 5.18e-06, 2.0]
    _enthalpy_constants = [5.6067, 0.38729]
