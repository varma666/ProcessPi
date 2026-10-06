from .base import Component
from processpi.units import *

class Trans2Methylcyclohexanol(Component):
    """
    Represents the properties and constants for trans2Methylcyclohexanol(C7?H14?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for trans2Methylcyclohexanol, which are essential for various process engineering calculations.
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
    name = "trans2Methylcyclohexanol"
    formula = "C7?H14?O"
    molecular_weight = 114.185

    # Critical properties
    _critical_temperature = Temperature(617.0, "K")
    _critical_pressure = Pressure(3.79, "MPa")
    _critical_volume = Volume(0.374, "m3")
    _critical_zc = 0.276
    _critical_acentric_factor = 0.679

    _density_constants = [0.72836, 0.27241, 617.0, 0.2478]
    _specific_heat_constants = [0.0, 447.99, 0.0, 0.0, 0.0, 2.5257, 3.1535]
    _viscosity_constants = [-6.6915, 3173.2, -1.3046]
    _thermal_conductivity_constants = [0.21828, -0.0002557]
    _vapor_pressure_constants = [54.179, 0.0, -4.22, 3.52e-18, 6.0]
    _enthalpy_constants = [7.8995, 0.42479]
