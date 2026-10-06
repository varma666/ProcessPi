from .base import Component
from processpi.units import *

class DiethylAmine(Component):
    """
    Represents the properties and constants for Diethyl amine(C4?H11?N).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Diethyl amine, which are essential for various process engineering calculations.
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
    name = "Diethyl amine"
    formula = "C4?H11?N"
    molecular_weight = 73.137

    # Critical properties
    _critical_temperature = Temperature(496.6, "K")
    _critical_pressure = Pressure(3.71, "MPa")
    _critical_volume = Volume(0.301, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.3039

    _density_constants = [0.85379, 0.25675, 496.6, 0.27027]
    _specific_heat_constants = [0.0, 243.18, 0.0, 0.0, 0.0, 1.5564, 1.8124]
    _viscosity_constants = [-17.57, 1385.7, 0.85647]
    _thermal_conductivity_constants = [0.2587, -0.00054343, 4.21e-07]
    _vapor_pressure_constants = [49.314, 0.0, -3.9256, 9.2e-18, 6.0]
    _enthalpy_constants = [4.6133, 0.42628]
