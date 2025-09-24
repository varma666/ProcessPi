# processpi/flowsheet.py

from typing import List, Dict, Union
from .equipment.base import Equipment
from .streams.material import MaterialStream
from .streams.energy import EnergyStream


class Flowsheet:
    """
    A simple flowsheet manager for sequential simulation.

    Responsibilities:
    - Hold equipment + streams
    - Define explicit connections
    - Run equipment in added order
    - Collect results for summary
    """

    def __init__(self, name: str):
        self.name = name
        self.equipment: List[Equipment] = []
        self.material_streams: List[MaterialStream] = []
        self.energy_streams: List[EnergyStream] = []
        self.connections: List[Dict[str, Union[Equipment, MaterialStream]]] = []

    # --------------------------
    # Add units + streams
    # --------------------------
    def add_equipment(self, unit: Equipment):
        self.equipment.append(unit)

    def add_material_stream(self, stream: MaterialStream):
        self.material_streams.append(stream)

    def add_energy_stream(self, stream: EnergyStream):
        self.energy_streams.append(stream)

    # --------------------------
    # Connections
    # --------------------------
    def connect(self, src, dst, port: str = "inlet"):
        """
        Connect streams or equipment.

        - (Stream → Equipment)
        - (Equipment → Stream)
        - (Equipment → Equipment)
        """
        if isinstance(src, MaterialStream) and isinstance(dst, Equipment):
            if port == "inlet":
                dst.inlets.append(src)
            elif port == "outlet":
                dst.outlets.append(src)
            else:
                raise ValueError("Invalid port name for Equipment.")
            self.connections.append({"from": src, "to": dst})

        elif isinstance(src, Equipment) and isinstance(dst, MaterialStream):
            src.outlets.append(dst)
            self.connections.append({"from": src, "to": dst})

        elif isinstance(src, Equipment) and isinstance(dst, Equipment):
            # simple 1-to-1 pipe assumption
            if src.outlets and dst.inlets:
                dst.inlets.append(src.outlets[0])
            self.connections.append({"from": src, "to": dst})

        else:
            raise ValueError("Unsupported connection type")

    # --------------------------
    # Simulation
    # --------------------------
    def run(self):
        for unit in self.equipment:
            result = unit.simulate()
            unit.last_results = result  # store for reporting

    def summary(self):
        print(f"\nFlowsheet: {self.name}")
        print("=" * 40)
        for unit in self.equipment:
            print(f"{unit.name} ({unit.__class__.__name__})")
            if hasattr(unit, "last_results"):
                for k, v in unit.last_results.items():
                    print(f"  {k}: {v}")
            print("-" * 30)
