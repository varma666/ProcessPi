from .base import Component
from processpi.units import *

class MethylisobutylKetone(Component):
    """
    Represents the properties and constants for Methylisobutyl ketone(C6?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methylisobutyl ketone, which are essential for various process engineering calculations.
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
    name = "Methylisobutyl ketone"
    formula = "C6?H12?O"
    molecular_weight = 100.159

    # Critical properties
    _critical_temperature = Temperature(574.6, "K")
    _critical_pressure = Pressure(3.27, "MPa")
    _critical_volume = Volume(0.369, "m3")
    _critical_zc = 0.253
    _critical_acentric_factor = 0.3557

    _density_constants = [0.71687, 0.26453, 574.6, 0.28918]
    _specific_heat_constants = [0.0, -79.862, 0.60769, 0.0, 0.0, 1.9029, 2.446]
    _viscosity_constants = [-11.394, 1168.7, -0.007539]
    _thermal_conductivity_constants = [0.2301, -0.00028899]
    _vapor_pressure_constants = [80.503, 0.0, -8.379, 1.81e-17, 6.0]
    _enthalpy_constants = [5.4687, 0.40583]
