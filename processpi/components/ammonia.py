from .base import Component
from processpi.units import *


class Ammonia(Component):
    """
    Represents the properties and constants for Ammonia ($NH_3$).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ammonia, which are essential for various process engineering calculations.
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
    name = "Ammonia"
    formula = "NH3"
    molecular_weight = 17.031
    
    # Critical properties for the compound
    _critical_temperature = Temperature(405.65, "K")
    _critical_pressure = Pressure(11.28, "MPa") 
    _critical_volume = Volume(0.07247, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.242  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2526  # Placeholder for critical acentric factor
    
    # Constants for various property correlations
    _density_constants = [3.5383, 0.25443, 405.65, 0.2888]
    _specific_heat_constants = [61.289,80925,799.4,-2651,0]
    _viscosity_constants = [-6.743,598.3,-0.7341,-3.69E-27, 10] 
    _thermal_conductivity_constants = [1.169, -0.002314, 0,0,0]
    _vapor_pressure_constants = [90.483, -4669.70, -11.607, 1.72E-02, 1] 
    _enthalpy_constants = [3.1523E-7, 0.3914, -0.2289,0.2309, 0]  # Placeholder for enthalpy constants
