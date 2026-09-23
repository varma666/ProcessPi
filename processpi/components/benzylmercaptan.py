from .base import Component
from processpi.units import *

class BenzylMercaptan(Component):
    """
    Represents the properties and constants for Benzyl mercaptan(C7?H8?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Benzyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Benzyl mercaptan"
    formula = "C7?H8?S"
    molecular_weight = 124.203

    # Critical properties
    _critical_temperature = Temperature(718.0, "K")
    _critical_pressure = Pressure(4.06, "MPa")
    _critical_volume = Volume(0.367, "m3")
    _critical_zc = 0.25
    _critical_acentric_factor = 0.3126

    _density_constants = [0.70797, 0.25982, 718.0, 0.32144]
    _specific_heat_constants = [0.0, 346.89, 0.0, 0.0, 0.0, 1.8494, 2.6406]
    _viscosity_constants = [-11.459, 1334.4, 0.00049694]
    _thermal_conductivity_constants = [0.20316, -0.00019912]
    _vapor_pressure_constants = [118.02, 0.0, -13.91, 6.48e-06, 2.0]
    _enthalpy_constants = [6.9642, 0.44354]
