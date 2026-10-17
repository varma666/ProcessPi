from .base import Component
from processpi.units import *

class MethylVinylEther(Component):
    """
    Represents the properties and constants for Methyl vinyl ether(C3H6O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl vinyl ether, which are essential for various process engineering calculations.
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
    name = "Methyl vinyl ether"
    formula = "C3H6O"
    molecular_weight = 58.079
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(437.0, "K")
    _critical_pressure = Pressure(4.67, "MPa")
    _critical_volume = Volume(0.21, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.2416

    _density_constants = [1.2587, 0.26433, 437.0, 0.25819]
    _specific_heat_constants = [73600, 184.7, 0.0, 0.0, 0.0]
    _viscosity_constants = [-10.34, 519.61, -0.013899, 0.0, 0.0]
    _thermal_conductivity_constants = [0.28035, -0.0004646, 0.0, 0.0, 0.0]
    _vapor_pressure_constants = [51.085, -4271, -4.307, 3.05e-17, 6.0]
    _enthalpy_constants = [3.587e-7, 0.3769, 0.0, 0.0, 0.0]
