from .base import Component, PropertyMethod
from processpi.units import *


class Ammonia(Component):
    """
    Represents the properties and constants for Ammonia ($NH_3$).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ammonia, which are essential for various process engineering calculations.
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
    name = "Ammonia"
    formula = "NH3"
    molecular_weight = 17.031
    
    # Critical properties for the compound
    _critical_temperature = Temperature(405.65, "K")
    _critical_pressure = Pressure(11.28, "MPa") 
    _critical_volume = Volume(0.07247, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.242  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2526  # Placeholder for critical acentric factor
    
    # Constants for various property correlations
    _density_constants = [3.5383, 0.25443, 405.65, 0.2888]
    # Liquid Cp, Perry's Chemical Engineers' Handbook, 8th ed., Table 2-153,
    # p. 2-165, "use Eq. (2)", 203.15-401.15 K (see specific_heat below).
    _specific_heat_constants = [61.289,80925,799.4,-2651,0]
    _viscosity_constants = [-6.743,598.3,-0.7341,-3.69E-27, 10] 
    _thermal_conductivity_constants = [1.169, -0.002314, 0,0,0]
    _vapor_pressure_constants = [90.483, -4669.70, -11.607, 1.72E-02, 1] 
    _enthalpy_constants = [3.1523E-7, 0.3914, -0.2289,0.2309, 0]  # Placeholder for enthalpy constants

    # Ideal-gas Cp, DIPPR Eq. 107, J/(kmol K), 100-1500 K, used by the base
    # class in the gas phase: Perry's 8th ed., Table 2-156, p. 2-176
    # (C1 = 0.33427E5, C2 = 0.4898E5, C3 = 2.036E3, C4 = 0.2256E5, C5 = 882).
    # 2090.7 J/kgK at 300 K.
    _ideal_gas_heat_capacity_constants = [0.33427E5, 0.4898E5, 2.036E3, 0.2256E5, 882]
    # `_thermal_conductivity_constants` above are the LIQUID ammonia
    # correlation (Table 2-315). In the gas phase the base class uses this:
    # vapour thermal conductivity, DIPPR Eq. 102, W/(m K), 200-900 K: Perry's
    # 8th ed., Table 2-314, p. 2-433 (C3, C4 blank). 0.0253 W/mK at 300 K.
    _vapor_thermal_conductivity_constants = [9.6608E-06, 1.3799, 0, 0]


    @PropertyMethod
    def specific_heat(self) -> SpecificHeat:
        if self._specific_heat is not None:
            return self._specific_heat
        cp_gas = self._ideal_gas_specific_heat()
        if cp_gas is not None:
            return cp_gas
        # Liquid: Perry's 8th ed., Table 2-153, Eq. (2), J/(kmol K):
        # Cp = C1^2/t + C2 - 2*C1*C3*t - C1*C4*t^2 - C3^2*t^3/3 - C3*C4*t^4/2 - C4^2*t^5/5
        # with t = 1 - T/Tc. Gives the table's 0.7575E5 at 203.15 K and 4.1847E5 at 401.15 K.
        C1, C2, C3, C4 = self._specific_heat_constants[:4]
        T = self.temperature.to("K").value
        t = 1 - T / self._critical_temperature.to("K").value
        cp = (C1 ** 2 / t) + C2 - (2 * C1 * C3 * t) - (C1 * C4 * t ** 2) - (C3 ** 2 * t ** 3 / 3) - (C3 * C4 * t ** 4 / 2) - (C4 ** 2 * t ** 5 / 5)
        return SpecificHeat(cp / self.molecular_weight, "J/kgK")

        
