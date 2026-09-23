from .base import Component
from processpi.units import *

class PropylAmine(Component):
    """
    Represents the properties and constants for Propyl amine(C3?H9?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Propyl amine, which are essential for various process engineering calculations.
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
    name = "Propyl amine"
    formula = "C3?H9?N"
    molecular_weight = 59.11

    # Critical properties
    _critical_temperature = Temperature(496.95, "K")
    _critical_pressure = Pressure(4.74, "MPa")
    _critical_volume = Volume(0.26, "m3")
    _critical_zc = 0.298
    _critical_acentric_factor = 0.2798

    _density_constants = [0.9195, 0.23878, 496.95, 0.2461]
    _specific_heat_constants = [0.0, 78.0, 0.0, 0.0, 0.0, 1.5422, 1.6605]
    _viscosity_constants = [-9.8074, 1010.4, -0.25697]
    _thermal_conductivity_constants = [0.2632, -0.0004278, 4.12e-07]
    _vapor_pressure_constants = [58.398, 0.0, -5.2876, 1.99e-06, 2.0]
    _enthalpy_constants = [4.4488, 0.39494]
