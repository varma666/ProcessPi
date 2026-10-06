from .base import Component
from processpi.units import *

class _12PropyleneGlycol(Component):
    """
    Represents the properties and constants for 12Propylene glycol(C3?H8?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 12Propylene glycol, which are essential for various process engineering calculations.
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
    name = "12Propylene glycol"
    formula = "C3?H8?O2?"
    molecular_weight = 76.094

    # Critical properties
    _critical_temperature = Temperature(626.0, "K")
    _critical_pressure = Pressure(6.1, "MPa")
    _critical_volume = Volume(0.239, "m3")
    _critical_zc = 0.28
    _critical_acentric_factor = 1.1065

    _density_constants = [1.0923, 0.26106, 626.0, 0.20459]
    _specific_heat_constants = [0.0, 445.2, 0.0, 0.0, 0.0, 1.5297, 2.6321]
    _viscosity_constants = [-804.54, 30487.0, 130.79, -0.15449, 1.0]
    _thermal_conductivity_constants = [0.2152, -4.97e-05]
    _vapor_pressure_constants = [212.8, 0.0, -28.109, 2.16e-05, 2.0]
    _enthalpy_constants = [8.07, 0.295]
