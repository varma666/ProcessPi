from .base import Component
from processpi.units import *

class _124Trimethylbenzene(Component):
    """
    Represents the properties and constants for 124Trimethylbenzene(C9?H12?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 124Trimethylbenzene, which are essential for various process engineering calculations.
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
    name = "124Trimethylbenzene"
    formula = "C9?H12?"
    molecular_weight = 120.192

    # Critical properties
    _critical_temperature = Temperature(649.1, "K")
    _critical_pressure = Pressure(3.232, "MPa")
    _critical_volume = Volume(0.43, "m3")
    _critical_zc = 0.258
    _critical_acentric_factor = 0.3787

    _density_constants = [0.60394, 0.25956, 649.1, 0.27713]
    _specific_heat_constants = [0.0, -128.47, 0.83741, 0.0, 0.0, 1.9338, 2.3642]
    _viscosity_constants = [-9.6461, 1281.2, -0.29478]
    _thermal_conductivity_constants = [0.19216, -0.0002105]
    _vapor_pressure_constants = [85.301, 0.0, -9.2166, 4.8e-06, 2.0]
    _enthalpy_constants = [5.9254, 0.35709]
