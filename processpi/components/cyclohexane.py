from .base import Component
from processpi.units import *

class Cyclohexane(Component):
    """
    Represents the properties and constants for Cyclohexane(C6H12).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Cyclohexane, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 65, in the equation forms `Component` uses. The
    liquid correlations start at the melting point, 279.69 K (6.5 C).

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
    - `_ideal_gas_heat_capacity_constants`: Ideal-gas Cp, used in the gas phase.
    - `_vapor_thermal_conductivity_constants`: Vapour thermal conductivity, used
      in the gas phase.
    """
    name = "Cyclohexane"
    formula = "C6H12"
    # Molecular weight and critical properties: Table 2-141, p. 2-139.
    molecular_weight = 84.159
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "cyclohexane"

    # Critical properties
    _critical_temperature = Temperature(553.8, "K")
    _critical_pressure = Pressure(4.08, "MPa")
    _critical_volume = Volume(0.308, "m3")
    _critical_zc = 0.273
    _critical_acentric_factor = 0.2081

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 279.69-553.8 K: Table 2-32, p. 2-99.
    _density_constants = [0.88998, 0.27376, 553.8, 0.28571]
    # Liquid Cp, polynomial, J/(kmol K), 279.69-400 K: Table 2-153, p. 2-166.
    _specific_heat_constants = [-220600, 3118.3, -9.4216, 0.010687, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 279.69-443.04 K: Table 2-313, p. 2-428.
    _viscosity_constants = [-33.763, 2497.2, 3.2236, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 279.69-353.87 K:
    # Table 2-315, p. 2-440.
    _thermal_conductivity_constants = [0.19813, -0.0002505, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 279.69-553.8 K: Table 2-8, p. 2-56.
    _vapor_pressure_constants = [51.087, -5226.4, -4.2278, 9.7554E-18, 6]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 279.69-553.8 K:
    # Table 2-150, p. 2-151 (C1 x 1E-07 = 4.4902).
    _enthalpy_constants = [4.4902E7, 0.39881, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K: Table 2-156, p. 2-177
    # (C1 = 0.432E5, C2 = 3.735E5, C3 = 1.192E3, C4 = 1.635E5, C5 = 530.1).
    _ideal_gas_heat_capacity_constants = [0.432E5, 3.735E5, 1.192E3, 1.635E5, 530.1]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 325-1000 K:
    # Table 2-314, p. 2-434.
    _vapor_thermal_conductivity_constants = [8.59E-7, 1.7709, 243, 0]
