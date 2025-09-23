# processpi/equipment/distillation.py

from __future__ import annotations
from typing import Optional, Dict
from .base import Equipment
from ..streams import MaterialStream


class DistillationColumn(Equipment):
    """
    Simplified Distillation Column (binary or multicomponent).
    
    Assumptions (initial version):
    - Steady-state.
    - Total condenser (distillate is liquid).
    - Partial reboiler (bottoms is liquid).
    - Uses constant relative volatility shortcut (Fenske-Underwood-Gilliland).
    - Feed at specified stage.
    - No rigorous stage-by-stage solving (yet).
    """

    def __init__(self, name: str, n_stages: int, feed_stage: int,
                 reflux_ratio: Optional[float] = None,
                 distillate_rate: Optional[float] = None):
        super().__init__(name)
        self.n_stages = n_stages
        self.feed_stage = feed_stage
        self.reflux_ratio = reflux_ratio
        self.distillate_rate = distillate_rate

        # Streams
        self.feed: Optional[MaterialStream] = None
        self.distillate: Optional[MaterialStream] = None
        self.bottoms: Optional[MaterialStream] = None

    def simulate(self) -> Dict:
        if self.feed is None or self.distillate is None or self.bottoms is None:
            raise ValueError(f"DistillationColumn {self.name} must have feed, distillate, and bottoms streams attached.")

        # --- Step 1: Material balance ---
        F = self.feed.flow
        if self.distillate_rate is not None:
            D = self.distillate_rate
            B = F - D
        else:
            raise ValueError("distillate_rate must be specified (initial version).")

        # --- Step 2: Split compositions using shortcut method ---
        z_feed = self.feed.composition  # dict: {component: mole fraction}
        xD, xB = {}, {}

        for comp, z in z_feed.items():
            # Simple split rule: more volatile → enriched in distillate
            if comp.relative_volatility >= 1.5:  # crude threshold
                xD[comp] = min(1.0, z * 1.5)
                xB[comp] = max(0.0, z - (xD[comp] * D / F))
            else:
                xB[comp] = min(1.0, z * 1.5)
                xD[comp] = max(0.0, z - (xB[comp] * B / F))

        # Normalize
        sum_xD = sum(xD.values())
        sum_xB = sum(xB.values())
        for comp in xD: xD[comp] /= sum_xD
        for comp in xB: xB[comp] /= sum_xB

        # --- Step 3: Copy to outlet streams ---
        self.distillate.copy_from(self.feed)
        self.distillate.flow = D
        self.distillate.composition = xD

        self.bottoms.copy_from(self.feed)
        self.bottoms.flow = B
        self.bottoms.composition = xB

        return {
            "feed_flow": F,
            "distillate_flow": D,
            "bottoms_flow": B,
            "distillate_composition": xD,
            "bottoms_composition": xB
        }
