from .base import Component
from processpi.units import *

class MethylisopropylEther(Component):
    """
    Represents the properties and constants for Methylisopropyl ether(C4?H10?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylisopropyl ether, which are essential for various process engineering calculations.
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
    name = "Methylisopropyl ether"
    formula = "C4?H10?O"
    molecular_weight = 74.122

    # Critical properties
    _critical_temperature = Temperature(464.48, "K")
    _critical_pressure = Pressure(3.762, "MPa")
    _critical_volume = Volume(0.276, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.2656

    _density_constants = [0.97887, 0.27017, 464.48, 0.28998]
    _specific_heat_constants = [0.0, -154.07, 0.7255, 0.0, 0.0, 1.356, 1.654]
    _viscosity_constants = [-11.216, 737.75, 0.019308]
    _thermal_conductivity_constants = [0.24154, -0.0003774]
    _vapor_pressure_constants = [53.867, 0.0, -4.7052, 2.88e-17, 6.0]
    _enthalpy_constants = [3.8501, 0.36453]
