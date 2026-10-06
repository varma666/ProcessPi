from .base import Component
from processpi.units import *

class TriethylAmine(Component):
    """
    Represents the properties and constants for Triethyl amine(C6?H15?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Triethyl amine, which are essential for various process engineering calculations.
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
    name = "Triethyl amine"
    formula = "C6?H15?N"
    molecular_weight = 101.19

    # Critical properties
    _critical_temperature = Temperature(535.15, "K")
    _critical_pressure = Pressure(3.04, "MPa")
    _critical_volume = Volume(0.39, "m3")
    _critical_zc = 0.266
    _critical_acentric_factor = 0.3162

    _density_constants = [0.7035, 0.27386, 535.15, 0.2872]
    _specific_heat_constants = [0.0, 368.13, 0.0, 0.0, 0.0, 1.8511, 2.4471]
    _viscosity_constants = [-3.7067, 585.78, -1.0926]
    _thermal_conductivity_constants = [0.1918, -0.0002453]
    _vapor_pressure_constants = [56.55, 0.0, -4.9815, 1.24e-17, 6.0]
    _enthalpy_constants = [4.664, 0.3663]
