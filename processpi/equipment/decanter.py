# processpi/equipment/decanter.py

from __future__ import annotations
from typing import Optional, Dict
from .base import Equipment
from ..streams import MaterialStream


class Decanter(Equipment):
    """
    Decanter (liquid–liquid phase separator).

    Assumptions:
    - Two immiscible liquid phases (e.g., water-rich and organic-rich).
    - Separation based on density: heavy phase → bottom, light phase → top.
    - User specifies split fractions OR component affinity (partitioning).
    - For now: simple split fraction for light/heavy phase.
    """

    def __init__(self, name: str, light_fraction: float = 0.5):
        super().__init__(name, inlet_ports=1, outlet_ports=2)
        self.light_fraction = light_fraction  # fraction of flow to light phase (0–1)

    def simulate(self) -> Dict:
        inlet: MaterialStream = self.inlets[0]
        if inlet is None:
            raise ValueError(f"Decanter {self.name} must have an inlet stream.")

        outlet_light: MaterialStream = self.outlets[0]
        outlet_heavy: MaterialStream = self.outlets[1]

        if outlet_light is None or outlet_heavy is None:
            raise ValueError(f"Decanter {self.name} must have two outlet streams attached.")

        F_total = inlet.flow
        z = inlet.composition.copy()

        # Flow split
        F_light = F_total * self.light_fraction
        F_heavy = F_total - F_light

        # For now: assume components split proportional to flow
        # (extend later with partition coefficients)
        outlet_light.copy_from(inlet)
        outlet_heavy.copy_from(inlet)

        outlet_light.flow = F_light
        outlet_heavy.flow = F_heavy

        # Normalize compositions (still same, just different flow basis)
        outlet_light.composition = {k: v for k, v in z.items()}
        outlet_heavy.composition = {k: v for k, v in z.items()}

        return {
            "F_in": F_total,
            "F_light": F_light,
            "F_heavy": F_heavy,
            "z_in": z,
            "z_light": outlet_light.composition,
            "z_heavy": outlet_heavy.composition,
        }
