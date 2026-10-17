from .base import Component
from processpi.units import *

class Oxygen(Component):
    """
    Represents the properties and constants for Oxygen(O2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Oxygen, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 275, in the equation forms `Component` uses.
    At 25 C and 1 atm oxygen is a gas: `specific_heat()` and
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
    name = "Oxygen"
    formula = "O2"
    # Molecular weight and critical properties: Table 2-141, p. 2-141.
    molecular_weight = 31.999
    # Heat exchanger data, read by Component.hx_data() and httype()
    # An oxidiser, not an inert gas: CORROSION_SEVERITY_DATABASE has no
    # oxidiser row, so it takes the generic low-medium "hydrocarbon" row.
    _hx_family = "inorganic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "vapor"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "oxygen"

    # Critical properties
    _critical_temperature = Temperature(154.58, "K")
    _critical_pressure = Pressure(5.043, "MPa")
    _critical_volume = Volume(0.0734, "m3")
    _critical_zc = 0.288
    _critical_acentric_factor = 0.0222

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 54.35-154.58 K: Table 2-32, p. 2-102.
    _density_constants = [3.9143, 0.28772, 154.58, 0.2924]
    # Liquid Cp, polynomial, J/(kmol K), 54.36-142 K: Table 2-153, p. 2-169.
    _specific_heat_constants = [175430, -6152.3, 113.92, -0.92382, 0.0027963]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 54.36-150 K: Table 2-313, p. 2-431.
    _viscosity_constants = [-4.1476, 94.04, -1.207, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 60-150 K:
    # Table 2-315, p. 2-443.
    _thermal_conductivity_constants = [0.2741, -0.00138, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 54.36-154.58 K: Table 2-8, p. 2-59.
    _vapor_pressure_constants = [51.245, -1200.2, -6.4361, 2.8405E-02, 1]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 54.36-154.58 K:
    # Table 2-150, p. 2-154 (C1 x 1E-07 = 0.9008).
    _enthalpy_constants = [9.008E6, 0.4542, -0.4096, 0.3183, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 50-1500 K: Table 2-156, p. 2-180
    # (C1 = 0.29103E5, C2 = 0.1004E5, C3 = 2.5265E3, C4 = 0.09356E5, C5 = 1153.8).
    _ideal_gas_heat_capacity_constants = [0.29103E5, 0.1004E5, 2.5265E3, 0.09356E5, 1153.8]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 80-2000 K:
    # Table 2-314, p. 2-437.
    _vapor_thermal_conductivity_constants = [0.00044994, 0.7456, 56.699, 0]
