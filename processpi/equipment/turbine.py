# processpi/equipment/turbine.py

from __future__ import annotations
from typing import Optional, Dict, Any
from .base import Equipment
from ..streams import MaterialStream
from ..units import Power


class Turbine(Equipment):
    """
    Gas-phase turbine / expander.

    Assumptions:
    - Single stage.
    - Isentropic expansion with efficiency correction.
    - Adiabatic (no heat exchange).
    - Shaft power is produced (negative duty to process).
    """

    def __init__(self, name: str,
                 isentropic_efficiency: float = 0.8,
                 outlet_pressure: Optional[float] = None,
                 pressure_ratio: Optional[float] = None):
        super().__init__(name, inlet_ports=1, outlet_ports=1)
        self.eta = isentropic_efficiency
        self.outlet_pressure = outlet_pressure
        self.pressure_ratio = pressure_ratio

    def simulate(self) -> Dict[str, Any]:
        inlet: MaterialStream = self.inlets[0]
        outlet: MaterialStream = self.outlets[0]

        if inlet is None or outlet is None:
            raise ValueError(f"{self.name}: Must have inlet and outlet streams connected.")

        if inlet.phase != "vapor":
            raise ValueError(f"{self.name}: Turbine requires vapor phase at inlet.")

        P1 = inlet.pressure.to("Pa").value
        T1 = inlet.temperature.to("K").value
        cp = inlet.get_property("cp")          # J/kg-K
        gamma = inlet.get_property("gamma")    # cp/cv
        m_dot = inlet.mass_flow().to("kg/s").value

        # Decide outlet pressure
        if self.outlet_pressure is not None:
            P2 = self.outlet_pressure.to("Pa").value
        elif self.pressure_ratio is not None:
            P2 = P1 / self.pressure_ratio
        else:
            raise ValueError("Must specify outlet_pressure or pressure_ratio.")

        if P2 >= P1:
            raise ValueError("Turbine must reduce pressure (P2 < P1).")

        # Ideal isentropic outlet temperature
        T2s = T1 * (P2 / P1) ** ((gamma - 1) / gamma)

        # Actual outlet temperature with efficiency
        T2 = T1 - self.eta * (T1 - T2s)

        # Shaft power produced
        w_dot = m_dot * cp * (T1 - T2)
        power = Power(w_dot, "W")

        # Update outlet stream
        outlet.copy_from(inlet)
        outlet.pressure = P2
        outlet.temperature.value = T2
        # Phase auto-updates (could condense if expansion is large)

        return {
            "inlet_P": P1,
            "outlet_P": P2,
            "Tin": T1,
            "Tout": T2,
            "m_dot": m_dot,
            "power": power,   # positive = produced
            "efficiency": self.eta
        }
