from .base import Component
from processpi.units import *
from CoolProp.CoolProp import PropsSI
from typing import Literal

class Steam(Component):
    name = "Steam"
    formula = "H2O"
    molecular_weight = 18.015

    def __init__(
        self,
        temperature: Temperature = None,
        pressure: Pressure = None,
        phase: Literal["liquid", "vapor"] = "vapor",
    ):
        super().__init__(temperature, pressure)
        self.phase = phase
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
            'CP', 
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
