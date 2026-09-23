from .base import Component
from processpi.units import *

class Oxylene(Component):
    """
    Represents the properties and constants for oXylene(C8?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for oXylene, which are essential for various process engineering calculations.
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
    name = "oXylene"
    formula = "C8?H10?"
    molecular_weight = 106.165

    # Critical properties
    _critical_temperature = Temperature(630.3, "K")
    _critical_pressure = Pressure(3.732, "MPa")
    _critical_volume = Volume(0.37, "m3")
    _critical_zc = 0.264
    _critical_acentric_factor = 0.3101

    _density_constants = [0.69962, 0.26143, 630.3, 0.27365]
    _specific_heat_constants = [0.0, 0.0, -2.63, 0.00302, 0.0, 1.7314, 2.2269]
    _viscosity_constants = [-15.489, 1393.5, 0.63711]
    _thermal_conductivity_constants = [0.19989, -0.0002299]
    _vapor_pressure_constants = [90.405, 0.0, -10.086, 5.96e-06, 2.0]
    _enthalpy_constants = [5.5395, 0.37788]
