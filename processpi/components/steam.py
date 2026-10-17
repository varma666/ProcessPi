from .base import Component
from processpi.units import *


class _LazyCoolProp:
    """CoolProp, imported on first use. Importing it takes about 4.6 s, and
    every `import processpi` paid that through this module even when Steam
    was never used."""

    def __getattr__(self, name):
        import CoolProp.CoolProp as module

        return getattr(module, name)


CP = _LazyCoolProp()
from typing import Literal

class Steam(Component):
    name = "Steam"
    hx_type = "steam"
    formula = "H2O"
    molecular_weight = 18.015
    # Heat exchanger data, read by Component.hx_data() and httype()
    _hx_family = "inorganic"
    _hx_liquid_type = "water"
    _hx_fouling_key = "steam"
    _hx_corrosion_key = "steam_condensate"
    _hx_vapor_type = "steam"

    def __init__(
        self,
        temperature: Temperature = None,
        pressure: Pressure = None,
        phase: Literal["liquid", "vapor"] = "vapor",
    ):
        # The phase goes to Component, so phase() still works: an instance
        # attribute named `phase` hid the phase() method ('str' object is not
        # callable).
        super().__init__(temperature, pressure, phase=phase)
        # Move critical properties to init to avoid module-level CP calls
        self._critical_temperature = Temperature(CP.PropsSI('Tcrit', 'Water'), "K")
        self._critical_pressure = Pressure(CP.PropsSI('Pcrit', 'Water'), "Pa")

    def density(self) -> Density:
        rho = CP.PropsSI(
            'D', 
            'T', self.temperature.value, 
            'P', self.pressure.value, 
            'Water'
        )
        return Density(rho, "kg/m3")

    def specific_heat(self) -> SpecificHeat:
        cp = CP.PropsSI(
            'CPMASS', 
            'T', self.temperature.value, 
            'P', self.pressure.value, 
            'Water'
        )
        return SpecificHeat(cp, "J/kgK")

    def viscosity(self) -> Viscosity:
        mu = CP.PropsSI(
            'V', 
            'T', self.temperature.value, 
            'P', self.pressure.value, 
            'Water'
        )
        return Viscosity(mu, "Pa·s")

    def thermal_conductivity(self) -> ThermalConductivity:
        k = CP.PropsSI(
            'L', 
            'T', self.temperature.value, 
            'P', self.pressure.value, 
            'Water'
        )
        return ThermalConductivity(k, "W/mK")

    def vapor_pressure(self) -> Pressure:
        vp = CP.PropsSI('P', 'T', self.temperature.value, 'Q', 0, 'Water')
        return Pressure(vp, "Pa")

    def enthalpy(self) -> HeatOfVaporization:
        h_liquid = CP.PropsSI('H', 'T', self.temperature.value, 'Q', 0, 'Water')
        h_vapor = CP.PropsSI('H', 'T', self.temperature.value, 'Q', 1, 'Water')
        hv = h_vapor - h_liquid
        return HeatOfVaporization(hv, "J/kg")
