from .base import Component
from processpi.units import *

class MethacrylicAcid(Component):
    """
    Represents the properties and constants for Methacrylic acid(C4?H6?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methacrylic acid, which are essential for various process engineering calculations.
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
    name = "Methacrylic acid"
    formula = "C4?H6?O2?"
    molecular_weight = 86.089

    # Critical properties
    _critical_temperature = Temperature(662.0, "K")
    _critical_pressure = Pressure(4.79, "MPa")
    _critical_volume = Volume(0.28, "m3")
    _critical_zc = 0.244
    _critical_acentric_factor = 0.3318

    _density_constants = [0.87025, 0.24383, 662.0, 0.28571]
    _specific_heat_constants = [0.0, -58.59, 0.3582, 0.0, 0.0, 1.5915, 1.8837]
    _viscosity_constants = [-14.527, 1497.7, 0.51747]
    _thermal_conductivity_constants = [0.2306, -0.00025201]
    _vapor_pressure_constants = [109.53, 0.0, -12.289, 3.2e-06, 2.0]
    _enthalpy_constants = [4.6095, 0.23331]
