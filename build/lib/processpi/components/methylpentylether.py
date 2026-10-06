from .base import Component
from processpi.units import *

class MethylPentylEther(Component):
    """
    Represents the properties and constants for Methyl pentyl ether(C6?H14?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl pentyl ether, which are essential for various process engineering calculations.
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
    name = "Methyl pentyl ether"
    formula = "C6?H14?O"
    molecular_weight = 102.175

    # Critical properties
    _critical_temperature = Temperature(546.49, "K")
    _critical_pressure = Pressure(3.042, "MPa")
    _critical_volume = Volume(0.38, "m3")
    _critical_zc = 0.254
    _critical_acentric_factor = 0.3442

    _density_constants = [0.71004, 0.26981, 546.49, 0.29974]
    _specific_heat_constants = [0.0, -468.32, 1.2209, 0.0, 0.0, 2.0728, 2.4663]
    _viscosity_constants = [-11.391, 1090.8, 1.08e-07]
    _thermal_conductivity_constants = [0.21698, -0.00028998]
    _vapor_pressure_constants = [61.907, 0.0, -5.706, 1.18e-17, 6.0]
    _enthalpy_constants = [5.0002, 0.3781]
