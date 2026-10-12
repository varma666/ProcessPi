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
    hx_type = "gas_low_pressure"
    formula = "Mixture"
    molecular_weight = 28.96
    
    # Critical properties for the compound
    _critical_temperature = Temperature(132.45, "K")
    _critical_pressure = Pressure(3.774, "MPa") 
    _critical_volume = Volume(0.09147, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.313  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0  # Placeholder for critical acentric factor
    
    # Constants for various property correlations
    _density_constants = [2.8963, 0.26733, 132.45,0.2734]
    _specific_heat_constants = [-214460,9185.1,-106.12,0.41616,0]
    _viscosity_constants = [-20.077, 285.15, 1.784,-6.2382E-22, 10] 
    _thermal_conductivity_constants = [0.28472, -0.0017393, 0,0,0]
    _vapor_pressure_constants = [21.662, -692.39, -0.392, 0.0047574, 1] 
    _enthalpy_constants = [0.8474E-7, 0.3822,0,0,0]  # Placeholder for enthalpy constants

    # `_specific_heat_constants` and `_thermal_conductivity_constants` above are
    # the LIQUID air correlations (Perry's Chemical Engineers' Handbook, 8th ed.,
    # Table 2-153, 75-115 K, and Table 2-315, 75-125 K). Above that range they
    # give Cp = 162857 J/kgK and a negative k at 35 C. In the gas phase the
    # base class uses these instead:
    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 50-1500 K: Perry's 8th ed.,
    # Table 2-156, p. 2-176 (C1 = 0.28958E5, C2 = 0.0939E5, C3 = 3.012E3,
    # C4 = 0.0758E5, C5 = 1484). 1001.2 J/kgK at 300 K.
    _ideal_gas_heat_capacity_constants = [0.28958E5, 0.0939E5, 3.012E3, 0.0758E5, 1484]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 70-2000 K: Perry's
    # 8th ed., Table 2-314, p. 2-433. 0.0261 W/mK at 300 K.
    _vapor_thermal_conductivity_constants = [0.00031417, 0.7786, -0.7116, 2121.7]
