from .base import Component
from processpi.units import *

class MalonicAcid(Component):
    """
    Represents the properties and constants for Malonic acid(C3?H4?O4?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Malonic acid, which are essential for various process engineering calculations.
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
    name = "Malonic acid"
    formula = "C3?H4?O4?"
    molecular_weight = 104.061

    # Critical properties
    _critical_temperature = Temperature(805.0, "K")
    _critical_pressure = Pressure(5.64, "MPa")
    _critical_volume = Volume(0.258, "m3")
    _critical_zc = 0.217
    _critical_acentric_factor = 0.9418

    _density_constants = [0.84266, 0.217, 805.0, 0.28571]
    _specific_heat_constants = [0.0, -41.619, 0.42817, 0.0, 0.0, 2.1213, 2.888]
    _viscosity_constants = [-19.834, 2784.5, 1.1161]
    _thermal_conductivity_constants = [0.28918, -0.0002614]
    _vapor_pressure_constants = [122.92, 0.0, -13.113, 2.06e-18, 6.0]
    _enthalpy_constants = [11.767, 0.37877]
