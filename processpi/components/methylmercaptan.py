from .base import Component
from processpi.units import *

class MethylMercaptan(Component):
    """
    Represents the properties and constants for Methyl mercaptan(CH4?S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl mercaptan, which are essential for various process engineering calculations.
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
    name = "Methyl mercaptan"
    formula = "CH4?S"
    molecular_weight = 48.107

    # Critical properties
    _critical_temperature = Temperature(469.95, "K")
    _critical_pressure = Pressure(7.23, "MPa")
    _critical_volume = Volume(0.145, "m3")
    _critical_zc = 0.268
    _critical_acentric_factor = 0.1582

    _density_constants = [1.9323, 0.28018, 469.95, 0.28523]
    _specific_heat_constants = [0.0, -263.23, 0.60412, 0.0, 0.0, 0.8939, 0.9052]
    _viscosity_constants = [-10.628, 645.0, 0.025885]
    _thermal_conductivity_constants = [0.26119, -0.00038345]
    _vapor_pressure_constants = [54.15, 0.0, -4.8127, 4.5e-17, 6.0]
    _enthalpy_constants = [3.4448, 0.37427]
