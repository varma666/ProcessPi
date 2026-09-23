from .base import Component
from processpi.units import *

class DimethylPhthalate(Component):
    """
    Represents the properties and constants for Dimethyl phthalate(C10?H10?O4?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dimethyl phthalate, which are essential for various process engineering calculations.
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
    name = "Dimethyl phthalate"
    formula = "C10?H10?O4?"
    molecular_weight = 194.184

    # Critical properties
    _critical_temperature = Temperature(766.0, "K")
    _critical_pressure = Pressure(2.78, "MPa")
    _critical_volume = Volume(0.53, "m3")
    _critical_zc = 0.231
    _critical_acentric_factor = 0.6568

    _density_constants = [0.47977, 0.25428, 766.0, 0.30722]
    _specific_heat_constants = [0.0, 325.75, 0.0, 0.0, 0.0, 2.9587, 3.2383]
    _viscosity_constants = [16.961, -423.16, -3.8178, 1360000000000000.0, -6.0]
    _thermal_conductivity_constants = [0.13905, 0.0001509, -3.98e-07]
    _vapor_pressure_constants = [72.517, 0.0, -6.755, 1.33e-06, 2.0]
    _enthalpy_constants = [8.1578, 0.29346]
