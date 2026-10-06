from .base import Component
from processpi.units import *

class EthyleneGlycol(Component):
    """
    Represents the properties and constants for Ethylene glycol(C2?H6?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylene glycol, which are essential for various process engineering calculations.
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
    name = "Ethylene glycol"
    formula = "C2?H6?O2?"
    molecular_weight = 62.068

    # Critical properties
    _critical_temperature = Temperature(720.0, "K")
    _critical_pressure = Pressure(8.2, "MPa")
    _critical_volume = Volume(0.191, "m3")
    _critical_zc = 0.262
    _critical_acentric_factor = 0.5068

    _density_constants = [1.315, 0.25125, 720.0, 0.21868]
    _specific_heat_constants = [0.0, 436.78, -0.18486, 0.0, 0.0, 1.3666, 2.0598]
    _viscosity_constants = [-20.515, 2468.5, 1.2435, 2500000000000.0, -5.0]
    _thermal_conductivity_constants = [0.088067, 0.00094712, -1.31e-06]
    _vapor_pressure_constants = [84.09, 0.0, -8.1976, 1.65e-18, 6.0]
    _enthalpy_constants = [8.3518, 0.42625]
