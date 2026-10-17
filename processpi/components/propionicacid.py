from .base import Component
from processpi.units import *

class PropionicAcid(Component):
    """
    Represents the properties and constants for Propionic Acid(CH3CH2COOH).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Propionic Acid, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 300, in the equation forms `Component` uses.

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
    name = "Propionic Acid"
    formula = "C3H6O2"
    # Molecular weight and critical properties: Table 2-141, p. 2-142.
    molecular_weight = 74.079
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "acid"
    _hx_velocity_key = "propionic_acid"

    # Critical properties
    _critical_temperature = Temperature(600.81, "K")
    _critical_pressure = Pressure(4.668, "MPa")
    _critical_volume = Volume(0.235, "m3")
    _critical_zc = 0.22
    _critical_acentric_factor = 0.5796

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 252.45-600.81 K: Table 2-32, p. 2-102.
    _density_constants = [1.0969, 0.25568, 600.81, 0.26857]
    # Liquid Cp, polynomial, J/(kmol K), 252.45-414.32 K: Table 2-153, p. 2-170.
    _specific_heat_constants = [213660, -702.7, 1.6605, 0, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 252.45-414.32 K: Table 2-313, p. 2-431.
    _viscosity_constants = [-23.931, 1834.6, 1.9124, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 252.45-543.15 K:
    # Table 2-315, p. 2-444.
    _thermal_conductivity_constants = [0.1954, -0.000164, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 252.45-600.81 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [54.552, -7149.4, -4.2769, 1.1843E-18, 6]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 252.45-600.81 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 4).
    _enthalpy_constants = [4E7, 1.3936, -2.9465, 1.794, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 298.15-1500 K: Table 2-156, p. 2-180
    # (C1 = 0.6959E5, C2 = 1.7778E5, C3 = 1.7098E3, C4 = 1.2654E5, C5 = 763.78).
    _ideal_gas_heat_capacity_constants = [0.6959E5, 1.7778E5, 1.7098E3, 1.2654E5, 763.78]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 414.32-1000 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [0.00022286, 0.91704, 678.21, 0]
