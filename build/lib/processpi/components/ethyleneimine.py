from .base import Component
from processpi.units import *

class Ethyleneimine(Component):
    """
    Represents the properties and constants for Ethyleneimine(C2?H5?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethyleneimine, which are essential for various process engineering calculations.
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
    name = "Ethyleneimine"
    formula = "C2?H5?N"
    molecular_weight = 43.068

    # Critical properties
    _critical_temperature = Temperature(537.0, "K")
    _critical_pressure = Pressure(6.85, "MPa")
    _critical_volume = Volume(0.173, "m3")
    _critical_zc = 0.265
    _critical_acentric_factor = 0.2007

    _density_constants = [1.3462, 0.23289, 537.0, 0.23357]
    _specific_heat_constants = [0.0, 205.35, 0.0, 0.0, 0.0, 0.9819, 1.1441]
    _viscosity_constants = [-11.012, 967.4]
    _thermal_conductivity_constants = [0.3097, -0.0004023]
    _vapor_pressure_constants = [66.51, 0.0, -6.3332, 1.04e-17, 6.0]
    _enthalpy_constants = [4.94, 0.466]
