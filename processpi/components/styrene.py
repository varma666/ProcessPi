from .base import Component
from processpi.units import *

class Styrene(Component):
    """
    Represents the properties and constants for Styrene(C6H5CH=CH2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Styrene, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    All constants are from Perry's Chemical Engineers' Handbook, 8th ed. (2008),
    Section 2, compound no. 312, in the equation forms `Component` uses.

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
    name = "Styrene"
    formula = "C8H8"
    # Molecular weight and critical properties: Table 2-141, p. 2-142.
    molecular_weight = 104.149
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "organic"
    _hx_liquid_type = "organic"
    _hx_fouling_key = "hydrocarbons"
    _hx_corrosion_key = "hydrocarbon"
    _hx_velocity_key = "styrene"

    # Critical properties
    _critical_temperature = Temperature(636, "K")
    _critical_pressure = Pressure(3.84, "MPa")
    _critical_volume = Volume(0.352, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.2971

    # Liquid density, DIPPR Eq. 105, kmol/m3 (times MW for kg/m3),
    # 242.54-636 K: Table 2-32, p. 2-103.
    _density_constants = [0.7397, 0.2603, 636, 0.3009]
    # Liquid Cp, polynomial, J/(kmol K), 242.54-418.31 K: Table 2-153, p. 2-170.
    _specific_heat_constants = [113340, 290.2, -0.6051, 0.0013567, 0]
    # Liquid viscosity, DIPPR Eq. 101, Pa s, 242.54-418.31 K: Table 2-313, p. 2-432.
    _viscosity_constants = [-22.675, 1758, 1.6701, 0, 0]
    # Liquid thermal conductivity, polynomial, W/(m K), 242.54-418.31 K:
    # Table 2-315, p. 2-444.
    _thermal_conductivity_constants = [0.20215, -0.0002201, 0, 0, 0]
    # Vapour pressure, DIPPR Eq. 101, Pa, 242.54-636 K: Table 2-8, p. 2-60.
    _vapor_pressure_constants = [105.93, -8685.9, -12.42, 7.5583E-06, 2]
    # Heat of vaporization, DIPPR Eq. 106, J/kmol, 242.54-636 K:
    # Table 2-150, p. 2-155 (C1 x 1E-07 = 5.726).
    _enthalpy_constants = [5.726E7, 0.4055, 0, 0, 0]

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K: Table 2-156, p. 2-181
    # (C1 = 0.893E5, C2 = 2.1503E5, C3 = 0.772E3, C4 = 0.999E5, C5 = 2442).
    _ideal_gas_heat_capacity_constants = [0.893E5, 2.1503E5, 0.772E3, 0.999E5, 2442]
    # Vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 418.31-1000 K:
    # Table 2-314, p. 2-438.
    _vapor_thermal_conductivity_constants = [0.010048, 0.4033, 553.74, 685570]
