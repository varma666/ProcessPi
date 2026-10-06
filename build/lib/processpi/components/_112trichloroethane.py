from .base import Component
from processpi.units import *

class _112Trichloroethane(Component):
    """
    Represents the properties and constants for 112Trichloroethane(C2?H3?Cl3?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 112Trichloroethane, which are essential for various process engineering calculations.
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
    name = "112Trichloroethane"
    formula = "C2?H3?Cl3?"
    molecular_weight = 133.404

    # Critical properties
    _critical_temperature = Temperature(602.0, "K")
    _critical_pressure = Pressure(4.48, "MPa")
    _critical_volume = Volume(0.281, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.2591

    _density_constants = [0.9062, 0.25475, 602.0, 0.31]
    _specific_heat_constants = [0.0, 159.3, 0.0, 0.0, 0.0, 1.4102, 1.5114]
    _viscosity_constants = [0.388, 736.5, -1.7063]
    _thermal_conductivity_constants = [0.20731, -0.00024997]
    _vapor_pressure_constants = [54.153, 0.0, -4.5383, 4.98e-18, 6.0]
    _enthalpy_constants = [5.0929, 0.38013]
