from .base import Component
from processpi.units import *

class ButylAcetate(Component):
    """
    Represents the properties and constants for Butyl acetate(C6?H12?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Butyl acetate, which are essential for various process engineering calculations.
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
    name = "Butyl acetate"
    formula = "C6?H12?O2?"
    molecular_weight = 116.158

    # Critical properties
    _critical_temperature = Temperature(575.4, "K")
    _critical_pressure = Pressure(3.09, "MPa")
    _critical_volume = Volume(0.389, "m3")
    _critical_zc = 0.251
    _critical_acentric_factor = 0.4394

    _density_constants = [0.67794, 0.2637, 575.4, 0.29318]
    _specific_heat_constants = [0.0, 384.52, 0.0, 0.0, 0.0, 2.2649, 2.6537]
    _viscosity_constants = [-17.488, 1478.2, 0.91828]
    _thermal_conductivity_constants = [0.21721, -0.00026563]
    _vapor_pressure_constants = [122.82, 0.0, -14.99, 1.05e-05, 2.0]
    _enthalpy_constants = [5.8276, 0.38854]
