from .base import Component
from processpi.units import *

class SuccinicAcid(Component):
    """
    Represents the properties and constants for Succinic acid(C4?H6?O4?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Succinic acid, which are essential for various process engineering calculations.
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
    name = "Succinic acid"
    formula = "C4?H6?O4?"
    molecular_weight = 118.088

    # Critical properties
    _critical_temperature = Temperature(806.0, "K")
    _critical_pressure = Pressure(4.71, "MPa")
    _critical_volume = Volume(0.317, "m3")
    _critical_zc = 0.223
    _critical_acentric_factor = 0.9922

    _density_constants = [0.70284, 0.22268, 806.0, 0.28571]
    _specific_heat_constants = [0.0, -236.96, 0.63148, 0.0, 0.0, 2.6961, 3.3228]
    _viscosity_constants = [-13.422, 3431.8]
    _thermal_conductivity_constants = [0.28215, -0.0002585]
    _vapor_pressure_constants = [128.65, 0.0, -13.872, 2.16e-18, 6.0]
    _enthalpy_constants = [12.018, 0.37149]
