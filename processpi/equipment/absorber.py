# processpi/equipment/absorber.py

from __future__ import annotations
from typing import Optional, Dict
from .base import Equipment
from ..streams import MaterialStream


class Absorber(Equipment):
    """
    Absorber Column.
    
    Removes solute from gas stream into a liquid solvent.
    
    Assumptions (initial version):
    - Steady state
    - Counter-current contact
    - Uses overall K-removal efficiency (fraction of solute absorbed)
    - Single major solute for simplicity (extendable to multicomponent)
    """

    def __init__(self, name: str, stages: int, removal_efficiency: float):
        super().__init__(name)
        self.stages = stages
        self.removal_efficiency = removal_efficiency  # 0–1 fraction

        # Streams
        self.gas_in: Optional[MaterialStream] = None
        self.gas_out: Optional[MaterialStream] = None
        self.liquid_in: Optional[MaterialStream] = None
        self.liquid_out: Optional[MaterialStream] = None

    def simulate(self) -> Dict:
        if (self.gas_in is None or self.gas_out is None or
            self.liquid_in is None or self.liquid_out is None):
            raise ValueError(f"Absorber {self.name} must have gas_in, gas_out, liquid_in, liquid_out streams.")

        F_gas = self.gas_in.flow
        F_liq = self.liquid_in.flow

        z_gas = self.gas_in.composition.copy()
        z_liq = self.liquid_in.composition.copy()

        # Pick solute (for demo: assume first component in gas is solute)
        solute = list(z_gas.keys())[0]

        # Apply removal efficiency
        solute_in_gas = z_gas[solute] * F_gas
        absorbed = solute_in_gas * self.removal_efficiency
        solute_out_gas = solute_in_gas - absorbed

        # Update outlet streams
        self.gas_out.copy_from(self.gas_in)
        self.liquid_out.copy_from(self.liquid_in)

        self.gas_out.flow = F_gas
        self.liquid_out.flow = F_liq + absorbed  # solute added to solvent

        # Adjust compositions
        self.gas_out.composition[solute] = solute_out_gas / F_gas
        self.liquid_out.composition[solute] = absorbed / self.liquid_out.flow

        return {
            "absorbed": absorbed,
            "gas_out_comp": self.gas_out.composition,
            "liq_out_comp": self.liquid_out.composition,
        }
