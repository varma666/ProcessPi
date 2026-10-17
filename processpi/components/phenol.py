from .base import Component
from processpi.units import *

class Phenol(Component):
    """
    Represents the properties and constants for Phenol(C6H5OH).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Phenol, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 291, in the equation forms `Component` uses.
    Perry's liquid correlations start at 314.06 K (40.9 C), where phenol
    melts; below that the model extrapolates the liquid, so at 25 C it
    reports a liquid although phenol is a solid there.

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
    name = "Phenol"
    formula = "C6H6O"
    # Molecular weight and critical properties: Table 2-141, p. 2-141.
    molecular_weight = 94.111
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "phenol"

    # Critical properties
    _critical_temperature = Temperature(694.25, "K")
    _critical_pressure = Pressure(6.13, "MPa")
    _critical_volume = Volume(0.229, "m3")
    _critical_zc = 0.243
    _critical_acentric_factor = 0.4435

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 314.06-694.25 K: Table 2-32, p. 2-102.
    _density_constants = [1.3798, 0.31598, 694.25, 0.32768]
    # Liquid Cp, polynomial, J/(kmol K), 314.06-425 K: Table 2-153, p. 2-169.
    _specific_heat_constants = [101720, 317.61, 0, 0, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 291.45-555.4 K: Table 2-313, p. 2-431.
    _viscosity_constants = [-43.335, 3881.7, 4.3983, 3.0548E+24, -10]
    # Liquid thermal conductivity, polynomial, W/(m K), 314.06-454.99 K:
    # Table 2-315, p. 2-443.
    _thermal_conductivity_constants = [0.18831, -0.0001, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 314.06-694.25 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [95.444, -10113, -10.09, 6.7603E-18, 6]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 314.06-694.25 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 7.306).
    _enthalpy_constants = [7.306E7, 0.4246, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K: Table 2-156, p. 2-180
    # (C1 = 0.434E5, C2 = 2.445E5, C3 = 1.152E3, C4 = 1.512E5, C5 = 507).
    _ideal_gas_heat_capacity_constants = [0.434E5, 2.445E5, 1.152E3, 1.512E5, 507]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 454.99-1000 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [0.038846, 0.2392, 985.81, 937170]
