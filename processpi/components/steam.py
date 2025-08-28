from .base import Component
from processpi.units import *
import CoolProp.CoolProp as CP
from typing import Literal

class Steam(Component):
    """
    Component class for Steam (H₂O) using the CoolProp library.

    This class provides accurate thermophysical properties for water
    across all phases (liquid, vapor, superheated, etc.) by leveraging
    the CoolProp library.
    """

    name = "Steam"
    formula = "H2O"
    molecular_weight = 18.015
    _critical_temperature = Temperature(CP.PropsSI('Tcrit', 'Water'), "K")
    _critical_pressure = Pressure(CP.PropsSI('Pcrit', 'Water'), "Pa")

    def __init__(
        self,
        temperature: Temperature = None,
        pressure: Pressure = None,
        phase: Literal["liquid", "vapor"] = "vapor",
    ):
        super().__init__(temperature, pressure)
        self.phase = phase

    def density(self) -> Density:
        """Density (kg/m³) using CoolProp."""
        rho = CP.PropsSI(
            'D', 
            'T', self.temperature.value, 
            'P', self.pressure.value, 
            'Water'
        )
        return Density(rho, "kg/m3")

    def specific_heat(self) -> SpecificHeat:
        """Specific heat (J/kg·K) using CoolProp."""
        cp = CP.PropsSI(
            'CP', 
            'T', self.temperature.value, 
            'P', self.pressure.value, 
            'Water'
        )
        return SpecificHeat(cp, "J/kgK")

    def viscosity(self) -> Viscosity:
        """Dynamic viscosity (Pa·s) using CoolProp."""
        mu = CP.PropsSI(
            'V', 
            'T', self.temperature.value, 
            'P', self.pressure.value, 
            'Water'
        )
        return Viscosity(mu, "Pa·s")

    def thermal_conductivity(self) -> ThermalConductivity:
        """Thermal conductivity (W/m·K) using CoolProp."""
        k = CP.PropsSI(
            'L', 
            'T', self.temperature.value, 
            'P', self.pressure.value, 
            'Water'
        )
        return ThermalConductivity(k, "W/mK")

    def vapor_pressure(self) -> Pressure:
        """Vapor pressure (Pa) using CoolProp."""
        # CoolProp provides saturation pressure as a function of temperature
        vp = CP.PropsSI('P', 'T', self.temperature.value, 'Q', 0, 'Water')
        return Pressure(vp, "Pa")

    def enthalpy(self) -> HeatOfVaporization:
        """Enthalpy of vaporization (J/kg) using CoolProp."""
        # Calculate latent heat from liquid and vapor enthalpies at saturation
        h_liquid = CP.PropsSI('H', 'T', self.temperature.value, 'Q', 0, 'Water')
        h_vapor = CP.PropsSI('H', 'T', self.temperature.value, 'Q', 1, 'Water')
        hv = h_vapor - h_liquid
        return HeatOfVaporization(hv, "J/kg")
