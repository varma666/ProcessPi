from .base import Component
from processpi.units import *

class MethylMethacrylate(Component):
    """
    Represents the properties and constants for Methyl methacrylate(C5?H8?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl methacrylate, which are essential for various process engineering calculations.
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
    name = "Methyl methacrylate"
    formula = "C5?H8?O2?"
    molecular_weight = 100.116

    # Critical properties
    _critical_temperature = Temperature(566.0, "K")
    _critical_pressure = Pressure(3.68, "MPa")
    _critical_volume = Volume(0.323, "m3")
    _critical_zc = 0.253
    _critical_acentric_factor = 0.2802

    _density_constants = [0.7761, 0.25068, 566.0, 0.29773]
    _specific_heat_constants = [0.0, -938.4, 2.413, 0.0, 0.0, 1.6611, 2.4118]
    _viscosity_constants = [-0.099, 496.0, -1.5939]
    _thermal_conductivity_constants = [0.2583, -0.000379]
    _vapor_pressure_constants = [107.36, 0.0, -12.72, 8.33e-06, 2.0]
    _enthalpy_constants = [5.468, 0.4472]
