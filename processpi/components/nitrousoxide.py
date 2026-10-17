from .base import Component
from processpi.units import *

class NitrousOxide(Component):
    """
    Represents the properties and constants for Nitrous Oxide(N2O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Nitrous Oxide, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 252, in the equation forms `Component` uses.
    At 25 C and 1 atm nitrous oxide is a gas: `specific_heat()` and
    `thermal_conductivity()` then use the ideal-gas Cp and the vapour k below,
    and `viscosity()` the base class's Sutherland fallback (air constants).

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
    name = "Nitrous Oxide"
    formula = "N2O"
    # Molecular weight and critical properties: Table 2-141, p. 2-141.
    molecular_weight = 44.013
    # Heat exchanger data, read by Component.hx_data() and httype()
    # An oxidiser, not an inert gas: CORROSION_SEVERITY_DATABASE has no
    # oxidiser row, so it takes the generic low-medium "hydrocarbon" row.
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "nitrous_oxide"

    # Critical properties
    _critical_temperature = Temperature(309.57, "K")
    _critical_pressure = Pressure(7.245, "MPa")
    _critical_volume = Volume(0.0974, "m3")
    _critical_zc = 0.274
    _critical_acentric_factor = 0.1409

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 182.3-309.57 K: Table 2-32, p. 2-102.
    _density_constants = [2.781, 0.27244, 309.57, 0.2882]
    # Liquid Cp, polynomial, J/(kmol K), 182.3-200 K: Table 2-153, p. 2-169.
    _specific_heat_constants = [67556, 54.373, 0, 0, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 210-283.09 K: Table 2-313, p. 2-431.
    _viscosity_constants = [19.329, -381.68, -4.8618, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), one value, at 277.59 K:
    # Table 2-315, p. 2-443.
    _thermal_conductivity_constants = [0.10112, 0, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 182.3-309.57 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [96.512, -4045, -12.277, 2.8860E-05, 2]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 182.3-309.57 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 2.3215).
    _enthalpy_constants = [2.3215E7, 0.384, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K: Table 2-156, p. 2-180
    # (C1 = 0.29338E5, C2 = 0.3236E5, C3 = 1.1238E3, C4 = 0.2177E5, C5 = 479.4).
    _ideal_gas_heat_capacity_constants = [0.29338E5, 0.3236E5, 1.1238E3, 0.2177E5, 479.4]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 182.3-1000 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [0.001096, 0.667, 540, 0]
