from .base import Component
from processpi.units import *

class HydrogenCyanide(Component):
    """
    Represents the properties and constants for Hydrogen Cyanide(HCN).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hydrogen Cyanide, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 186, in the equation forms `Component` uses.
    Hydrogen cyanide boils just above 25 C at 1 atm, so at 25 C and 1 atm
    the vapour-pressure test gives a liquid and at 30 C a gas.

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
    name = "Hydrogen Cyanide"
    formula = "HCN"
    # Molecular weight and critical properties: Table 2-141, p. 2-140.
    molecular_weight = 27.025
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "hydrogen_cyanide"

    # Critical properties
    _critical_temperature = Temperature(456.65, "K")
    _critical_pressure = Pressure(5.39, "MPa")
    _critical_volume = Volume(0.139, "m3")
    _critical_zc = 0.197
    _critical_acentric_factor = 0.4099

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 259.83-456.65 K: Table 2-32, p. 2-101.
    _density_constants = [1.3413, 0.18589, 456.65, 0.28206]
    # Liquid Cp, polynomial, J/(kmol K), 259.83-298.85 K: Table 2-153, p. 2-168.
    _specific_heat_constants = [95398, -197.52, 0.3883, 0, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 259.83-298.85 K: Table 2-313, p. 2-430.
    _viscosity_constants = [-21.927, 1266.5, 1.5927, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 259.83-298.85 K:
    # Table 2-315, p. 2-442.
    _thermal_conductivity_constants = [0.43454, -0.0007008, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 259.83-456.65 K: Table 2-8, p. 2-58.
    _vapor_pressure_constants = [36.75, -3927.1, -2.1245, 3.8948E-17, 6]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 259.83-456.65 K:
    # Table 2-150, p. 2-153 (C1 x 1E-07 = 3.349).
    _enthalpy_constants = [3.349E7, 0.2053, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K: Table 2-156, p. 2-179
    # (C1 = 0.30125E5, C2 = 0.3171E5, C3 = 1.6102E3, C4 = 0.2179E5, C5 = 626).
    _ideal_gas_heat_capacity_constants = [0.30125E5, 0.3171E5, 1.6102E3, 0.2179E5, 626]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 273.15-673.15 K:
    # Table 2-314, p. 2-436.
    _vapor_thermal_conductivity_constants = [4.6496E-06, 1.3669, -210.76, 58295]
