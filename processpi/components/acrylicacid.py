from .base import Component
from processpi.units import *


class AcrylicAcid(Component):
    """
    Represents the properties and constants for Acrylic Acid ($C_3H_4O_2$).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Acrylic Acid, which are essential for various process engineering calculations.
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
    name = "Acrylic Acid"
    formula = "C3H4O2"
    molecular_weight = 72.063
    
    # Critical properties for the compound
    _critical_temperature = Temperature(615, "K")
    _critical_pressure = Pressure(5.66, "MPa") 
    _critical_volume = Volume(0.208, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.23  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.5383  # Placeholder for critical acentric factor
    
    # Constants for various property correlations
    _density_constants = [1.2414, 0.25822, 615,0.30701]
    _specific_heat_constants = [55300,300,0,0,0]
    _viscosity_constants = [-28.12, 2280.2, 2.3956, 0, 0] 
    _thermal_conductivity_constants = [0.2441, -0.0002904, 0,0,0]
    _vapor_pressure_constants = [46.745, -6587.1, -3.2208, 0.00000052253, 2] 
    _enthalpy_constants = [4.3756E-7, 2.2571,-4.5116,2.5738, 0]  # Placeholder for enthalpy constants
