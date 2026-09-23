from .base import Component
from processpi.units import *

class DimethylAcetylene(Component):
    """
    Represents the properties and constants for Dimethyl acetylene(C4?H6?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dimethyl acetylene, which are essential for various process engineering calculations.
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
    name = "Dimethyl acetylene"
    formula = "C4?H6?"
    molecular_weight = 54.09

    # Critical properties
    _critical_temperature = Temperature(473.2, "K")
    _critical_pressure = Pressure(4.87, "MPa")
    _critical_volume = Volume(0.221, "m3")
    _critical_zc = 0.274
    _critical_acentric_factor = 0.2385

    _density_constants = [1.1717, 0.25895, 473.2, 0.27289]
    _specific_heat_constants = [0.0, 124.16, 0.0, 0.0, 0.0, 1.1806, 1.2542]
    _viscosity_constants = [0.10842, 300.2, -1.6831]
    _thermal_conductivity_constants = [0.22773, -0.00034804]
    _vapor_pressure_constants = [66.592, 0.0, -6.8387, 6.68e-06, 2.0]
    _enthalpy_constants = [3.856, 0.3737]
