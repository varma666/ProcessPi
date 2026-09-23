from .base import Component
from processpi.units import *

class _12Dichloropropane(Component):
    """
    Represents the properties and constants for 12Dichloropropane(C3?H6?Cl2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 12Dichloropropane, which are essential for various process engineering calculations.
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
    name = "12Dichloropropane"
    formula = "C3?H6?Cl2?"
    molecular_weight = 112.986

    # Critical properties
    _critical_temperature = Temperature(572.0, "K")
    _critical_pressure = Pressure(4.24, "MPa")
    _critical_volume = Volume(0.291, "m3")
    _critical_zc = 0.259
    _critical_acentric_factor = 0.2564

    _density_constants = [0.89833, 0.26142, 572.0, 0.2868]
    _specific_heat_constants = [0.0, 149.44, 0.0, 0.0, 0.0, 1.5266, 1.6678]
    _viscosity_constants = [-11.269, 1195.3, 0.012736]
    _thermal_conductivity_constants = [0.19653, -0.00025012]
    _vapor_pressure_constants = [65.955, 0.0, -6.5509, 4.32e-06, 2.0]
    _enthalpy_constants = [4.675, 0.36529]
