from .base import Component
from processpi.units import *

class Heptanal(Component):
    """
    Represents the properties and constants for Heptanal(C7H14O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Heptanal, which are essential for various process engineering calculations.
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
    name = "Heptanal"
    formula = "C7H14O"
    molecular_weight = 114.185
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"

    # Critical properties
    _critical_temperature = Temperature(616.8, "K")
    _critical_pressure = Pressure(3.16, "MPa")
    _critical_volume = Volume(0.434, "m3")
    _critical_zc = 0.267
    _critical_acentric_factor = 0.4279

    _density_constants = [0.59006, 0.25609, 616.8, 0.28384]
    _specific_heat_constants = [222360, -105.17, 0.65074, 0.0, 0.0]
    _viscosity_constants = [-10.443, 1063.2, -0.031488, 0, 0]
    _thermal_conductivity_constants = [0.21816, -0.0003015, 1.03e-07, 0, 0]
    _vapor_pressure_constants = [92.252, -8349, -10.274, 5.93e-06, 2.0]
    _enthalpy_constants = [5.956e-7, 0.36474, 0, 0, 0]
