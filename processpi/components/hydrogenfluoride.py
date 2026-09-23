from .base import Component
from processpi.units import *

class HydrogenFluoride(Component):
    """
    Represents the properties and constants for Hydrogen fluoride(HF).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hydrogen fluoride, which are essential for various process engineering calculations.
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
    name = "Hydrogen fluoride"
    formula = "HF"
    molecular_weight = 20.006

    # Critical properties
    _critical_temperature = Temperature(461.15, "K")
    _critical_pressure = Pressure(6.48, "MPa")
    _critical_volume = Volume(0.069, "m3")
    _critical_zc = 0.117
    _critical_acentric_factor = 0.3823

    _density_constants = [2.5635, 0.1766, 461.15, 0.3733]
    _specific_heat_constants = [0.0, -223.02, 0.6297, 0.0, 0.0, 0.4288, 0.5119]
    _viscosity_constants = [353.99, 13928.0, -41.717, 0.0, -0.5]
    _thermal_conductivity_constants = [0.7516, -0.0010874]
    _vapor_pressure_constants = [59.544, 0.0, -6.1764, 1.42e-05, 2.0]
    _enthalpy_constants = [13.451, 13.36, -23.383, 10.785]
