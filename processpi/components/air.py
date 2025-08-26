from .base import Component
from processpi.units import *


class Air(Component):
    """
    Represents the properties and constants for Air (a molecular mixture).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Air, which are essential for various process engineering calculations.
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
    name = "Air"
    formula = "Mixture"
    molecular_weight = 28.96
    
    # Critical properties for the compound
    _critical_temperature = Temperature(132.45, "K")
    _critical_pressure = Pressure(3.774, "MPa") 
    _critical_volume = Volume(0.09147, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.313  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0  # Placeholder for critical acentric factor
    
    # Constants for various property correlations
    _density_constants = [0.26733, 132.45, 0.27341,59.15]
    _specific_heat_constants = [-214460,9185.1,-106.12,0.41616,0]
    _viscosity_constants = [-20.077, 285.15, 1.784,-6.2382E-22, 10] 
    _thermal_conductivity_constants = [0.28472, -0.0017393, 0,0,0]
    _vapor_pressure_constants = [21.662, -692.39, -0.392, 0.0047574, 1] 
    _enthalpy_constants = [0.3822E-7, 59.15,0.6759,132.45, 0]  # Placeholder for enthalpy constants
