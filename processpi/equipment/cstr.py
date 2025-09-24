from __future__ import annotations
from typing import Optional, Dict, Any
from .base import Equipment
from ..streams import MaterialStream


class CSTR(Equipment):
    """
    Continuous Stirred Tank Reactor (CSTR).

    Assumptions:
    - Perfect mixing (outlet composition = reactor composition).
    - Steady-state operation.
    - Reaction kinetics placeholder (rate function can be injected).
    """

    def __init__(self, name: str, volume: float, rate_fn: Optional[callable] = None):
        super().__init__(name)
        self.volume = volume
        self.rate_fn = rate_fn

    def simulate(self) -> Dict[str, Any]:
        inlet: MaterialStream = self.inlet
        outlet: MaterialStream = self.outlet

        if inlet is None or outlet is None:
            raise ValueError(f"CSTR {self.name} must have inlet and outlet streams.")

        outlet.copy_from(inlet)

        if self.rate_fn:
            rates = self.rate_fn(outlet, outlet.temperature, outlet.pressure)
            outlet.apply_reaction(rates, residence_time=self.volume / inlet.volumetric_flow)

        return {
            "type": "CSTR",
            "inlet_T": inlet.temperature,
            "outlet_T": outlet.temperature,
            "inlet_F": inlet.mass_flow,
            "outlet_F": outlet.mass_flow
        }
