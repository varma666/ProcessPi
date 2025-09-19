# processpi/equipment/valve.py

from __future__ import annotations
from typing import Optional
from .base import Equipment
from ..streams import MaterialStream

class Valve(Equipment):
    """
    Valve / Throttle for pressure reduction.
    
    Assumptions:
    - Isenthalpic process (h_in = h_out).
    - No shaft work, no heat exchange.
    - Temperature and phase updates handled by MaterialStream via Component.
    """

    def __init__(self, name: str, delta_p: Optional[float] = None, outlet_pressure: Optional[float] = None):
        super().__init__(name)
        self.delta_p = delta_p
        self.outlet_pressure = outlet_pressure

    def simulate(self):
        inlet: MaterialStream = self.inlet
        outlet: MaterialStream = self.outlet

        if inlet is None or outlet is None:
            raise ValueError(f"Valve {self.name} must have inlet and outlet streams attached.")

        # Decide outlet pressure
        if self.outlet_pressure is not None:
            P_out = self.outlet_pressure
        elif self.delta_p is not None:
            P_out = inlet.pressure - self.delta_p
        else:
            raise ValueError("Either delta_p or outlet_pressure must be specified.")

        if P_out <= 0:
            raise ValueError("Outlet pressure must be positive.")

        # Isenthalpic expansion: copy enthalpy
        h_in = inlet.enthalpy  # MaterialStream provides enthalpy from component + T
        outlet.copy_from(inlet)
        outlet.pressure = P_out

        # Enthalpy same, T and phase auto-updated by MaterialStream/component
        outlet.update_from_enthalpy(h_in, P_out)

        return {
            "inlet_P": inlet.pressure,
            "outlet_P": outlet.pressure,
            "enthalpy": h_in
        }
