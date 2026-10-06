from .base import Component
from processpi.units import *

class EthylisopropylKetone(Component):
    """
    Represents the properties and constants for Ethylisopropyl ketone(C6?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethylisopropyl ketone, which are essential for various process engineering calculations.
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
    name = "Ethylisopropyl ketone"
    formula = "C6?H12?O"
    molecular_weight = 100.159

    # Critical properties
    _critical_temperature = Temperature(567.0, "K")
    _critical_pressure = Pressure(3.32, "MPa")
    _critical_volume = Volume(0.369, "m3")
    _critical_zc = 0.26
    _critical_acentric_factor = 0.3891

    _density_constants = [0.68162, 0.25152, 567.0, 0.3182]
    _specific_heat_constants = [0.0, -404.54, 1.1382, 0.0, 0.0, 1.941, 2.4295]
    _viscosity_constants = [-11.452, 1172.7, -0.00010095]
    _thermal_conductivity_constants = [0.22873, -0.0002913]
    _vapor_pressure_constants = [57.459, 0.0, -4.9545, 5.2e-18, 6.0]
    _enthalpy_constants = [5.2207, 0.34893]
