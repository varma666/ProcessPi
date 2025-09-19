from __future__ import annotations
from typing import List, Dict, Any
from .base import Equipment
from ..streams import MaterialStream


class Splitter(Equipment):
    """
    Splits one MaterialStream into multiple outlets.
    Assumptions:
    - Perfect splitting (no additional energy effects).
    - Pressure drop neglected (outlet P = inlet P).
    """

    def __init__(self, name: str, num_outlets: int = 2, fractions: List[float] = None):
        super().__init__(name, inlet_ports=1, outlet_ports=num_outlets)
        if fractions is None:
            fractions = [1.0 / num_outlets] * num_outlets
        if abs(sum(fractions) - 1.0) > 1e-6:
            raise ValueError("Fractions must sum to 1.")
        self.fractions = fractions

    def simulate(self) -> Dict[str, Any]:
        inlet: MaterialStream = self.inlets[0]
        if inlet is None or any(o is None for o in self.outlets):
            raise ValueError(f"{self.name}: Inlet and all outlets must be connected.")

        m_in = inlet.mass_flow().to("kg/s").value
        results = {}

        for frac, out in zip(self.fractions, self.outlets):
            out.copy_from(inlet)
            out.mass_flow_value = m_in * frac  # assume MaterialStream has setter
            results[out.name] = {
                "mass_flow": out.mass_flow_value,
                "T": out.temperature.value,
                "P": out.pressure.to("Pa").value,
                "phase": out.phase,
            }

        return results
