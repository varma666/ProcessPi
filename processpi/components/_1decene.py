from .base import Component
from processpi.units import *

class _1Decene(Component):
    """
    Represents the properties and constants for 1Decene(C10?H20?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Decene, which are essential for various process engineering calculations.
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
    name = "1Decene"
    formula = "C10?H20?"
    molecular_weight = 140.266

    # Critical properties
    _critical_temperature = Temperature(616.6, "K")
    _critical_pressure = Pressure(2.223, "MPa")
    _critical_volume = Volume(0.584, "m3")
    _critical_zc = 0.253
    _critical_acentric_factor = 0.4805

    _density_constants = [0.43981, 0.25661, 616.6, 0.29148]
    _specific_heat_constants = [0.0, 0.0, 5.3948, -0.004348, 0.0, 2.7541, 3.825]
    _viscosity_constants = [-15.868, 1434.8, 0.68071]
    _thermal_conductivity_constants = [0.20237, -0.00024187]
    _vapor_pressure_constants = [68.401, 0.0, -6.4637, 6.38e-18, 6.0]
    _enthalpy_constants = [6.6985, 0.76944, -0.79975, 0.42379]
