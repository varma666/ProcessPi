from .base import Component
from processpi.units import *


class Acetone(Component):
    """
    Represents the properties and constants for Acetone ($C_3H_6O$).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acetone, which are essential for various process engineering calculations.
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
    name = "Acetone"
    formula = "C3H6O"
    molecular_weight = 58.080
    
    # Critical properties for the compound
    _critical_temperature = Temperature(508.1, "K")
    _critical_pressure = Pressure(4.701, "MPa")
    _critical_volume = Volume(0.209, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.233  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.3065  # Placeholder for critical acentric factor
    
    # Constants for various property correlations
    _density_constants = [1.2332, 0.25886, 508.2, 0.2913]
    _specific_heat_constants = [135600,-177,0.2837,0.000689,0]
    _viscosity_constants = [-14.918, 1023.4, 0.5961, 0, 0] 
    _thermal_conductivity_constants = [0.2878, -0.000427, 0,0,0]
    _vapor_pressure_constants = [69.006, -5599.6, -7.0985, 0.0000062237, 2] 
    _enthalpy_constants = [4.215E-7, 0.3397, 178.45, 3.639, 0]  # Placeholder for enthalpy constants
