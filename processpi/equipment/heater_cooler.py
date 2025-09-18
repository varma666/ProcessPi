from typing import Optional, Dict, Any
from ..streams import MaterialStream
from .base import Equipment


class HeatTransferUnit(Equipment):
    """
    Base class for heater/cooler type units.
    Supports sensible + latent heating/cooling.

    Energy balance:
        Q_total = m * cp * ΔT   [+/- m * Hvap if phase change occurs]

    Auto-detects phase change if outlet T crosses boiling point.
    """

    def __init__(self, name: str, mode: str = "heater"):
        super().__init__(name, inlet_ports=1, outlet_ports=1)
        self.mode = mode  # "heater" or "cooler"

    def _latent_heat(self, stream: MaterialStream) -> float:
        """Get latent heat of vaporization for the stream (J/kg)."""
        if not stream.components:
            return 0.0

        Hvap_mix = 0.0
        for comp, frac in stream.components.items():
            prop = stream.component_properties.get(comp, {})
            Hvap = prop.get("Hvap", None)
            if callable(Hvap):
                Hvap_val = Hvap(stream.temperature.value)
            else:
                Hvap_val = Hvap or 0.0
            Hvap_mix += frac * Hvap_val
        return Hvap_mix

    def _boiling_point(self, stream: MaterialStream) -> Optional[float]:
        """
        Estimate boiling point (K) from components.
        If multiple components, take weighted average.
        """
        if not stream.components:
            return None

        Tb_mix = 0.0
        for comp, frac in stream.components.items():
            prop = stream.component_properties.get(comp, {})
            Tb = prop.get("Tb", None)  # Boiling point property
            if callable(Tb):
                Tb_val = Tb(stream.pressure.value)
            else:
                Tb_val = Tb or None
            if Tb_val:
                Tb_mix += frac * Tb_val

        return Tb_mix if Tb_mix > 0 else None

    def simulate(
        self,
        heat_duty: Optional[float] = None,
        outlet_temperature: Optional[float] = None,
        outlet_phase: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Simulate heater/cooler.

        Parameters:
        - heat_duty (W) [optional]
        - outlet_temperature (float, K) [optional]
        - outlet_phase ("liquid" or "vapor") [optional, auto-detected if not provided]

        Returns:
        - dict with results: Q_total, Q_sensible, Q_latent, Tin, Tout, phase_in, phase_out
        """
        inlet = self.inlets[0]
        outlet = self.outlets[0]

        if inlet is None or outlet is None:
            raise ValueError(f"{self.name}: Must have both inlet and outlet connected.")

        m_dot = inlet.mass_flow().to("kg/s").value
        cp = inlet.get_property("cp")  # J/kg-K

        Tin = inlet.temperature.value
        Tout = outlet.temperature.value if outlet.temperature else None
        Qin_total = 0.0
        Q_sensible = 0.0
        Q_latent = 0.0

        # -------------------------
        # Case 1: Duty specified
        # -------------------------
        if heat_duty is not None:
            dT = heat_duty / (m_dot * cp)
            Tout = Tin + dT
            Qin_total = heat_duty
            Q_sensible = heat_duty

        # -------------------------
        # Case 2: Outlet T specified
        # -------------------------
        elif outlet_temperature is not None:
            Tout = outlet_temperature
            Q_sensible = m_dot * cp * (Tout - Tin)
            Qin_total = Q_sensible

        else:
            raise ValueError("Must specify either heat_duty or outlet_temperature.")

        # -------------------------
        # Phase detection
        # -------------------------
        phase_in = inlet.phase or "liquid"
        phase_out = outlet_phase or phase_in

        Tb = self._boiling_point(inlet)

        if Tb:  # Only auto-detect if boiling point available
            if Tin < Tb <= Tout:  # heating crosses boiling point
                Hvap = self._latent_heat(inlet)
                Q_latent = m_dot * Hvap
                Qin_total += Q_latent
                phase_out = "vapor"

            elif Tin > Tb >= Tout:  # cooling crosses boiling point
                Hvap = self._latent_heat(inlet)
                Q_latent = -m_dot * Hvap
                Qin_total += Q_latent
                phase_out = "liquid"

        outlet.phase = phase_out
        outlet.temperature.value = Tout

        # Flip sign for cooler
        if self.mode == "cooler" and Qin_total > 0:
            Qin_total *= -1
            Q_sensible *= -1
            Q_latent *= -1

        return {
            "Q_total": Qin_total,
            "Q_sensible": Q_sensible,
            "Q_latent": Q_latent,
            "Tin": Tin,
            "Tout": Tout,
            "phase_in": phase_in,
            "phase_out": outlet.phase,
            "Tb": Tb,
            "cp": cp,
            "m_dot": m_dot,
        }


class Heater(HeatTransferUnit):
    def __init__(self, name: str):
        super().__init__(name, mode="heater")


class Cooler(HeatTransferUnit):
    def __init__(self, name: str):
        super().__init__(name, mode="cooler")
