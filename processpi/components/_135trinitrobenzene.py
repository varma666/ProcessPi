from .base import Component
from processpi.units import *

class _135Trinitrobenzene(Component):
    """
    Represents the properties and constants for 135Trinitrobenzene(C6?H3?N3?O6?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 135Trinitrobenzene, which are essential for various process engineering calculations.
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
    name = "135Trinitrobenzene"
    formula = "C6?H3?N3?O6?"
    molecular_weight = 213.105

    # Critical properties
    _critical_temperature = Temperature(846.0, "K")
    _critical_pressure = Pressure(3.39, "MPa")
    _critical_volume = Volume(0.479, "m3")
    _critical_zc = 0.231
    _critical_acentric_factor = 0.8623

    _density_constants = [0.48195, 0.23093, 846.0, 0.28571]
    _specific_heat_constants = [0.0, 664.46, 0.0, 0.0, 0.0, 3.0508, 3.5629]
    _viscosity_constants = [-10.707, 1818.5]
    _thermal_conductivity_constants = [0.18421, -0.00016097]
    _vapor_pressure_constants = [506.33, 0.0, -69.22, 2.74e-05, 2.0]
    _enthalpy_constants = [10.687, 0.38]
