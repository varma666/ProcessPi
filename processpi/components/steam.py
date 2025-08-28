from .base import Component
from processpi.units import *
import pandas as pd
from typing import Literal

# Load steam tables from three different files
_STEAM_TABLES_SAT_T = pd.read_csv("processpi/data/steam_table_sat_T.csv", index_col=0)
_STEAM_TABLES_SAT_P = pd.read_csv("processpi/data/steam_table_sat_P.csv", index_col=0)
_STEAM_TABLES_SUP = pd.read_csv("processpi/data/steam_table_sup.csv", index_col=[0, 1])


class Steam(Component):
    """
    Component class for Steam (H₂O) using comprehensive steam tables.

    This class uses three separate steam table files for accurate property
    calculations across saturated, superheated, and compressed liquid regions.
    """

    name = "Steam"
    formula = "H2O"
    molecular_weight = 18.015
    _critical_temperature = Temperature(647.096, "K")
    _critical_pressure = Pressure(22.06, "MPa")

    def __init__(
        self,
        temperature: Temperature = None,
        pressure: Pressure = None,
        phase: Literal["liquid", "vapor"] = "vapor",
    ):
        super().__init__(temperature, pressure)
        self.phase = phase

    def _get_property_from_steam_table(self, prop: str):
        """Helper to get a property from the appropriate steam table."""
        T_C = self.temperature.value - 273.15  # Convert to °C
        P_bar = self.pressure.value / 1e5  # Convert to bar

        # Check for saturation conditions based on provided T or P
        sat_data_T = _STEAM_TABLES_SAT_T.iloc[(_STEAM_TABLES_SAT_T.index - T_C).abs().argsort()[:1]]
        sat_P_from_T = sat_data_T["P(bar)"].item()

        # Is it a saturated state?
        if abs(P_bar - sat_P_from_T) < 1e-2:  # Tolerance for floating point
            if self.phase == "liquid":
                return sat_data_T[f"{prop}L"].item()
            else:
                return sat_data_T[f"{prop}V"].item()

        # If not saturated, check for superheated/compressed liquid
        # Find the closest T and P in the combined table
        try:
            temp_idx = (
                _STEAM_TABLES_SUP.index.get_level_values(0) - T_C
            ).abs().argsort()[:1].item()
            press_idx = (
                _STEAM_TABLES_SUP.index.get_level_values(1) - P_bar
            ).abs().argsort()[:1].item()
            
            # Select the correct row based on the nearest T and P indices
            row_data = _STEAM_TABLES_SUP.iloc[temp_idx].iloc[press_idx]
            return row_data[prop]
        except KeyError:
            # This handles cases where the exact (T,P) pair is not found.
            # You may want to add interpolation or a more robust error message here.
            raise ValueError(
                f"Properties for T={T_C}°C and P={P_bar} bar not found in tables."
            )

    def density(self) -> Density:
        """Density of steam/water (kg/m³) from steam tables."""
        rho = self._get_property_from_steam_table("rho")
        return Density(rho, "kg/m3")

    def specific_heat(self) -> SpecificHeat:
        """Specific heat (J/kg·K) from steam tables."""
        cp = self._get_property_from_steam_table("Cp") * 1000  # kJ/kgK to J/kgK
        return SpecificHeat(cp, "J/kgK")

    def viscosity(self) -> Viscosity:
        """Dynamic viscosity (Pa·s) from steam tables."""
        mu = self._get_property_from_steam_table("mu") * 1e-6  # µPa·s to Pa·s
        return Viscosity(mu, "Pa·s")

    def thermal_conductivity(self) -> ThermalConductivity:
        """Thermal conductivity (W/m·K) from steam tables."""
        k = self._get_property_from_steam_table("k")
        return ThermalConductivity(k, "W/mK")

    def vapor_pressure(self) -> Pressure:
        """Vapor pressure (Pa) from steam tables (for saturated conditions)."""
        T_C = self.temperature.value - 273.15  # Convert to °C
        data = _STEAM_TABLES_SAT_T.iloc[(_STEAM_TABLES_SAT_T.index - T_C).abs().argsort()[:1]]
        vp = data["P(bar)"].item() * 1e5  # bar to Pa
        return Pressure(vp, "Pa")

    def enthalpy(self) -> HeatOfVaporization:
        """Enthalpy of vaporization (J/kg) from steam tables."""
        T_C = self.temperature.value - 273.15  # Convert to °C
        data = _STEAM_TABLES_SAT_T.iloc[(_STEAM_TABLES_SAT_T.index - T_C).abs().argsort()[:1]]
        hv = (data["hV"].item() - data["hL"].item()) * 1000  # kJ/kg to J/kg
        return HeatOfVaporization(hv, "J/kg")
