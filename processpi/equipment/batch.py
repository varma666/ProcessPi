from __future__ import annotations
from typing import Optional, Dict, Any
from .base import Equipment
from ..streams import MaterialStream


class BatchReactor(Equipment):
    """
    Batch Reactor.

    Assumptions:
    - Closed system (no inlet/outlet during reaction).
    - Time-dependent simulation.
    - Reaction integrated over given time.
    """

    def __init__(self, name: str, volume: float, rate_fn: Optional[callable] = None):
        super().__init__(name)
        self.volume = volume
        self.rate_fn = rate_fn

    def simulate(self, time: float = 1.0, steps: int = 10) -> Dict[str, Any]:
        stream: MaterialStream = self.inlet  # batch uses "inlet" as initial contents

        if stream is None:
            raise ValueError(f"BatchReactor {self.name} requires a feed MaterialStream as initial contents.")

        if self.rate_fn:
            dt = time / steps
            for _ in range(steps):
                rates = self.rate_fn(stream, stream.temperature, stream.pressure)
                stream.apply_reaction(rates, residence_time=dt)

        return {
            "type": "BatchReactor",
            "final_T": stream.temperature,
            "final_F": stream.mass_flow,
            "time": time
        }
