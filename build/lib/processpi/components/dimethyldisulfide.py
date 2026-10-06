from .base import Component
from processpi.units import *

class DimethylDisulfide(Component):
    """
    Represents the properties and constants for Dimethyl disulfide(C2?H6?S2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dimethyl disulfide, which are essential for various process engineering calculations.
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
    name = "Dimethyl disulfide"
    formula = "C2?H6?S2?"
    molecular_weight = 94.199

    # Critical properties
    _critical_temperature = Temperature(615.0, "K")
    _critical_pressure = Pressure(5.36, "MPa")
    _critical_volume = Volume(0.252, "m3")
    _critical_zc = 0.264
    _critical_acentric_factor = 0.2059

    _density_constants = [1.1058, 0.27866, 615.0, 0.31082]
    _specific_heat_constants = [0.0, -256.67, 0.5727, 0.0, 0.0, 1.4355, 1.534]
    _viscosity_constants = [-10.577, 1172.6, -0.14244]
    _thermal_conductivity_constants = [0.21373, -0.0002447]
    _vapor_pressure_constants = [81.045, 0.0, -8.777, 5.55e-06, 2.0]
    _enthalpy_constants = [4.9825, 0.3958]
