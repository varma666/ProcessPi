from typing import Optional, Dict, Any
from ..streams import MaterialStream
from .base import Equipment


class HeatTransferUnit(Equipment):
    """
    Base class for heater/cooler type units.
    Supports sensible + latent heating/cooling.
    Energy balance:
        Q = m * cp * ΔT   [+/- m * Hvap if phase change occurs]
    """

    def __init__(self, name: str, mode: str = "heater"):
        super().__init__(name, inlet_ports=1, outlet_ports=1)
        self.mode = mode  # "heater" or "cooler"

    def simulate(
        self,
        heat_duty: Optional[float] = None,
        outlet_temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Simulate heater/cooler.

        Parameters:
        - heat_duty (W) [optional]
        - outlet_temperature (float) [optional]

        Returns:
        - dict with results: Q (W), Tin, Tout, phase_in, phase_out
        """
        inlet = self.inlets[0]
        outlet = self.outlets[0]

        if inlet is None or outlet is None:
            raise ValueError(f"{self.name}: Must have both inlet and outlet connected.")

        m_dot = inlet.mass_flow().to("kg/s").value
        cp = inlet.get_property("cp")  # J/kg-K

        Tin = inlet.temperature.value
        Tout = outlet.temperature.value if outlet.temperature else None
        Qin = 0.0

        # -------------------------
        # Case 1: Duty specified
        # -------------------------
        if heat_duty is not None:
            dT = heat_duty / (m_dot * cp)
            Tout = Tin + dT
            Qin = heat_duty

        # -------------------------
        # Case 2: Outlet T specified
        # -------------------------
        elif outlet_temperature is not None:
            Tout = outlet_temperature
            Qin = m_dot * cp * (Tout - Tin)

        else:
            raise ValueError("Must specify either heat_duty or outlet_temperature.")

        # Update outlet temperature — phase is auto-updated by MaterialStream
        outlet.temperature.value = Tout

        # Flip sign for cooler
        if self.mode == "cooler" and Qin > 0:
            Qin *= -1

        return {
            "Q": Qin,
            "Tin": Tin,
            "Tout": Tout,
            "phase_in": inlet.phase,
            "phase_out": outlet.phase,  # comes directly from stream's auto-detection
            "cp": cp,
            "m_dot": m_dot,
        }


class Heater(HeatTransferUnit):
    def __init__(self, name: str):
        super().__init__(name, mode="heater")


class Cooler(HeatTransferUnit):
    def __init__(self, name: str):
        super().__init__(name, mode="cooler")
