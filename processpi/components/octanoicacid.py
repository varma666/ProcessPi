from .base import Component
from processpi.units import *

class OctanoicAcid(Component):
    """
    Represents the properties and constants for Octanoic acid(C8?H16?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Octanoic acid, which are essential for various process engineering calculations.
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
    name = "Octanoic acid"
    formula = "C8?H16?O2?"
    molecular_weight = 144.211

    # Critical properties
    _critical_temperature = Temperature(694.26, "K")
    _critical_pressure = Pressure(2.779, "MPa")
    _critical_volume = Volume(0.523, "m3")
    _critical_zc = 0.252
    _critical_acentric_factor = 0.7706

    _density_constants = [0.48251, 0.25196, 694.26, 0.26842]
    _specific_heat_constants = [0.0, 44.392, 0.8956, 0.0, 0.0, 2.9326, 4.6358]
    _viscosity_constants = [-60.795, 4617.8, 7.028]
    _thermal_conductivity_constants = [0.203, -0.0002]
    _vapor_pressure_constants = [140.16, 0.0, -16.004, 6.42e-18, 6.0]
    _enthalpy_constants = [12.23, 0.69294, 0.12287, -0.36132]
