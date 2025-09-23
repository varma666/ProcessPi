# processpi/equipment/stripper.py

from __future__ import annotations
from typing import Optional, Dict
from .base import Equipment
from ..streams import MaterialStream


class Stripper(Equipment):
    """
    Stripper Column.
    
    Removes solute from liquid stream into vapor/steam.
    
    Assumptions (initial version):
    - Steady state
    - Counter-current contact
    - Uses overall stripping efficiency (fraction of solute removed)
    - Single major solute for simplicity (extendable later)
    """

    def __init__(self, name: str, stages: int, stripping_efficiency: float):
        super().__init__(name)
        self.stages = stages
        self.stripping_efficiency = stripping_efficiency  # 0–1 fraction

        # Streams
        self.liquid_in: Optional[MaterialStream] = None
        self.liquid_out: Optional[MaterialStream] = None
        self.vapor_in: Optional[MaterialStream] = None
        self.vapor_out: Optional[MaterialStream] = None

    def simulate(self) -> Dict:
        if (self.liquid_in is None or self.liquid_out is None or
            self.vapor_in is None or self.vapor_out is None):
            raise ValueError(f"Stripper {self.name} must have liquid_in, liquid_out, vapor_in, vapor_out streams.")

        F_liq = self.liquid_in.flow
        F_vap = self.vapor_in.flow

        z_liq = self.liquid_in.composition.copy()
        z_vap = self.vapor_in.composition.copy()

        # Pick solute (first liquid component as solute)
        solute = list(z_liq.keys())[0]

        # Apply stripping efficiency
        solute_in_liq = z_liq[solute] * F_liq
        stripped = solute_in_liq * self.stripping_efficiency
        solute_out_liq = solute_in_liq - stripped

        # Update outlet streams
        self.liquid_out.copy_from(self.liquid_in)
        self.vapor_out.copy_from(self.vapor_in)

        self.liquid_out.flow = F_liq
        self.vapor_out.flow = F_vap + stripped

        # Adjust compositions
        self.liquid_out.composition[solute] = solute_out_liq / F_liq
        self.vapor_out.composition[solute] = stripped / self.vapor_out.flow

        return {
            "stripped": stripped,
            "liq_out_comp": self.liquid_out.composition,
            "vap_out_comp": self.vapor_out.composition,
        }
