from .base import Component
from processpi.units import *

class Methylcyclohexane(Component):
    """
    Represents the properties and constants for Methylcyclohexane(C7?H14?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylcyclohexane, which are essential for various process engineering calculations.
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
    name = "Methylcyclohexane"
    formula = "C7?H14?"
    molecular_weight = 98.186

    # Critical properties
    _critical_temperature = Temperature(572.1, "K")
    _critical_pressure = Pressure(3.48, "MPa")
    _critical_volume = Volume(0.369, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.2361

    _density_constants = [0.73109, 0.26971, 572.1, 0.29185]
    _specific_heat_constants = [0.0, -63.1, 0.8125, 0.0, 0.0, 1.3955, 1.9435]
    _viscosity_constants = [-11.358, 1213.1]
    _thermal_conductivity_constants = [0.1791, -0.0002291]
    _vapor_pressure_constants = [92.684, 0.0, -10.695, 8.14e-06, 2.0]
    _enthalpy_constants = [4.7528, 0.39437]
