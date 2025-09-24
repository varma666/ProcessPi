from __future__ import annotations
from typing import Optional, Dict, Any
from .base import Equipment
from ..streams import MaterialStream


class PFR(Equipment):
    """
    Plug Flow Reactor (PFR).

    Assumptions:
    - Steady state.
    - No axial mixing, plug flow behavior.
    - Discretized segments for reaction.
    """

    def __init__(self, name: str, volume: float, n_segments: int = 10, rate_fn: Optional[callable] = None):
        super().__init__(name)
        self.volume = volume
        self.n_segments = n_segments
        self.rate_fn = rate_fn

    def simulate(self) -> Dict[str, Any]:
        inlet: MaterialStream = self.inlet
        outlet: MaterialStream = self.outlet

        if inlet is None or outlet is None:
            raise ValueError(f"PFR {self.name} must have inlet and outlet streams.")

        outlet.copy_from(inlet)

        if self.rate_fn:
            segment_volume = self.volume / self.n_segments
            for _ in range(self.n_segments):
                rates = self.rate_fn(outlet, outlet.temperature, outlet.pressure)
                outlet.apply_reaction(rates, residence_time=segment_volume / outlet.volumetric_flow)

        return {
            "type": "PFR",
            "inlet_T": inlet.temperature,
            "outlet_T": outlet.temperature,
            "inlet_F": inlet.mass_flow,
            "outlet_F": outlet.mass_flow
        }
