from __future__ import annotations
from typing import List, Dict, Any
from .base import Equipment
from ..streams import MaterialStream


class Mixer(Equipment):
    """
    Mixer for combining multiple MaterialStreams into one.
    Assumptions:
    - Perfect mixing.
    - Energy balance for outlet T.
    - Pressure drop neglected (outlet P = min of inlets).
    """

    def __init__(self, name: str, num_inlets: int = 2):
        super().__init__(name, inlet_ports=num_inlets, outlet_ports=1)

    def simulate(self) -> Dict[str, Any]:
        if any(s is None for s in self.inlets) or self.outlets[0] is None:
            raise ValueError(f"{self.name}: All inlets and outlet must be connected.")

        outlet: MaterialStream = self.outlets[0]

        # Mass & energy balance
        m_total = 0.0
        h_total = 0.0

        pressures = []
        for s in self.inlets:
            m = s.mass_flow().to("kg/s").value
            h = s.enthalpy  # J/kg, T-dependent from Component
            m_total += m
            h_total += m * h
            pressures.append(s.pressure.to("Pa").value)

        if m_total <= 0:
            raise ValueError("Total mass flow in Mixer is zero or negative.")

        h_out = h_total / m_total
        P_out = min(pressures)  # assume outlet P = lowest inlet pressure

        # Copy one inlet as base
        outlet.copy_from(self.inlets[0])
        outlet.pressure = P_out
        outlet.update_from_enthalpy(h_out, P_out)

        return {
            "m_total": m_total,
            "h_out": h_out,
            "P_out": P_out,
            "T_out": outlet.temperature.value,
            "phase": outlet.phase
        }
