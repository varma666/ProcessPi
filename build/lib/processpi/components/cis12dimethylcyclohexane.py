from .base import Component
from processpi.units import *

class Cis12Dimethylcyclohexane(Component):
    """
    Represents the properties and constants for cis12Dimethylcyclohexane(C8?H16?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for cis12Dimethylcyclohexane, which are essential for various process engineering calculations.
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
    name = "cis12Dimethylcyclohexane"
    formula = "C8?H16?"
    molecular_weight = 112.213

    # Critical properties
    _critical_temperature = Temperature(606.15, "K")
    _critical_pressure = Pressure(2.938, "MPa")
    _critical_volume = Volume(0.46, "m3")
    _critical_zc = 0.268
    _critical_acentric_factor = 0.2324

    _density_constants = [0.52953, 0.24358, 606.15, 0.26809]
    _specific_heat_constants = [0.0, -62.38, 0.8851, 0.0, 0.0, 1.8029, 2.687]
    _viscosity_constants = [-11.796, 1463.5]
    _thermal_conductivity_constants = [0.18092, -0.0002108]
    _vapor_pressure_constants = [78.952, 0.0, -8.4344, 4.5e-06, 2.0]
    _enthalpy_constants = [5.2852, 0.41607]
