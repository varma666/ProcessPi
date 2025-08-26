from .base import Component
from processpi.units import *


class AceticAcid(Component):
    """
    Represents the properties and constants for Acetic Acid ($CH_3COOH$).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acetic Acid, which are essential for various process engineering calculations.
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
    name = "Acetic Acid"
    formula = "CH3COOH"
    molecular_weight = 60.052
    
    # Critical properties for the compound
    _critical_temperature = Temperature(591.95, "K")
    _critical_pressure = Pressure(5.786, "MPa") 
    _critical_volume = Volume(0.177, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.208  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.4665  # Placeholder for critical acentric factor
    
    # Constants for various property correlations
    _density_constants = [1.4486, 0.25892, 591.95, 0.2529]
    _specific_heat_constants = [139640,-320.8,0.8985,0,0]
    _viscosity_constants = [-9.03, 1212.3, -0.322, 0, 0] 
    _thermal_conductivity_constants = [0.214, -0.0001834, 0,0,0]
    _vapor_pressure_constants = [53.27, -6304.5, -4.2985, 8.8865E-18, 6] 
    _enthalpy_constants = [4.0179E-7, 2.6037, -5.0031,2.7069, 0]  # Placeholder for enthalpy constants
