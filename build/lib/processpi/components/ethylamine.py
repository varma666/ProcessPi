from .base import Component
from processpi.units import *

class EthylAmine(Component):
    """
    Represents the properties and constants for Ethyl amine(C2?H7?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethyl amine, which are essential for various process engineering calculations.
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
    name = "Ethyl amine"
    formula = "C2?H7?N"
    molecular_weight = 45.084

    # Critical properties
    _critical_temperature = Temperature(456.15, "K")
    _critical_pressure = Pressure(5.62, "MPa")
    _critical_volume = Volume(0.207, "m3")
    _critical_zc = 0.307
    _critical_acentric_factor = 0.2848

    _density_constants = [1.0936, 0.22636, 456.15, 0.25522]
    _specific_heat_constants = [0.0, 38.993, 0.0, 0.0, 0.0, 1.2919, 1.33]
    _viscosity_constants = [19.822, -0.12598, -4.9793]
    _thermal_conductivity_constants = [0.30059, -0.000581, 6.6e-07]
    _vapor_pressure_constants = [81.56, 0.0, -9.0779, 8.79e-06, 2.0]
    _enthalpy_constants = [4.275, 0.5857, -0.332, 0.169]
