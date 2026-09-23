from .base import Component
from processpi.units import *

class EthyleneOxide(Component):
    """
    Represents the properties and constants for Ethylene oxide(C2?H4?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylene oxide, which are essential for various process engineering calculations.
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
    name = "Ethylene oxide"
    formula = "C2?H4?O"
    molecular_weight = 44.053

    # Critical properties
    _critical_temperature = Temperature(469.15, "K")
    _critical_pressure = Pressure(7.19, "MPa")
    _critical_volume = Volume(0.140296, "m3")
    _critical_zc = 0.25876
    _critical_acentric_factor = 0.1974

    _density_constants = [1.836, 0.26024, 469.15, 0.2696]
    _specific_heat_constants = [0.0, -758.87, 2.8261, -0.003064, 0.0, 0.8303, 0.8693]
    _viscosity_constants = [-8.521, 634.2, -0.3314]
    _thermal_conductivity_constants = [0.26957, -0.0003984]
    _vapor_pressure_constants = [91.944, 0.0, -11.682, 0.0149, 1.0]
    _enthalpy_constants = [3.6652, 0.37878]
