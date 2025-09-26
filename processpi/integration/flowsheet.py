# processpi/flowsheet.py

from typing import List, Dict, Union
from ..equipment.base import Equipment
from ..streams.material import MaterialStream
from ..streams.energy import EnergyStream
from collections import defaultdict, deque


class Flowsheet:
    """
    A flowsheet manager for sequential simulation.

    Responsibilities:
    - Hold equipment + streams
    - Define explicit connections
    - Auto-build execution order from connections
    - Run equipment automatically
    - Collect results for summary
    """

    def __init__(self, name: str):
        self.name = name
        self.equipment: List[Equipment] = []
        self.material_streams: List[MaterialStream] = []
        self.energy_streams: List[EnergyStream] = []
        self.connections: List[Dict[str, Union[Equipment, MaterialStream, EnergyStream]]] = []

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
    def connect(self, src, dst, port: str):
        """
        Connect equipment and streams via named ports.

        - (Stream → Equipment, port="inlet1" or "energy_in1")
        - (Equipment → Stream, port="outlet1" or "energy_out1")
        - (Equipment → Equipment, port="inletX" or "energy_inX")
        """
        if isinstance(src, MaterialStream) and isinstance(dst, Equipment):
            dst.inlets[port] = src
            self.connections.append({"from": src, "to": dst, "port": port})

        elif isinstance(src, EnergyStream) and isinstance(dst, Equipment):
            dst.energy_in[port] = src
            self.connections.append({"from": src, "to": dst, "port": port})

        elif isinstance(src, Equipment) and isinstance(dst, MaterialStream):
            src.outlets[port] = dst
            self.connections.append({"from": src, "to": dst, "port": port})

        elif isinstance(src, Equipment) and isinstance(dst, EnergyStream):
            src.energy_out[port] = dst
            self.connections.append({"from": src, "to": dst, "port": port})

        elif isinstance(src, Equipment) and isinstance(dst, Equipment):
            # Infer correct connection based on port prefix
            if port.startswith("inlet"):
                dst.inlets[port] = list(src.outlets.values())[0]  # take first outlet
            elif port.startswith("energy_in"):
                dst.energy_in[port] = list(src.energy_out.values())[0]  # take first energy outlet
            else:
                raise ValueError("Invalid port name for Equipment → Equipment connection.")
            self.connections.append({"from": src, "to": dst, "port": port})

        else:
            raise ValueError("Unsupported connection type")

    # --------------------------
    # Dependency graph
    # --------------------------
    def _build_dependency_graph(self):
        """Build graph of unit dependencies based on connections"""
        graph = defaultdict(list)
        indegree = {u.name: 0 for u in self.equipment}

        for conn in self.connections:
            src, dst = conn["from"], conn["to"]

            if isinstance(src, Equipment) and isinstance(dst, Equipment):
                graph[src.name].append(dst.name)
                indegree[dst.name] += 1

            elif isinstance(src, (MaterialStream, EnergyStream)) and isinstance(dst, Equipment):
                # Stream → Equipment (dependency comes from its producer)
                pass

            elif isinstance(src, Equipment) and isinstance(dst, (MaterialStream, EnergyStream)):
                # Equipment → Stream (stream is not an executable unit)
                pass

        return graph, indegree

    def _topological_order(self):
        """Return equipment execution order"""
        graph, indegree = self._build_dependency_graph()
        queue = deque([u.name for u in self.equipment if indegree[u.name] == 0])
        order = []

        while queue:
            u = queue.popleft()
            order.append(u)
            for v in graph[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)

        if len(order) != len(self.equipment):
            raise RuntimeError("Cyclic dependency detected!")

        return order

    # --------------------------
    # Simulation
    # --------------------------
    def run(self):
        order = self._topological_order()
        name_to_unit = {u.name: u for u in self.equipment}

        for uname in order:
            unit = name_to_unit[uname]
            print(f"➡️ Running {unit.name} ({unit.__class__.__name__})")
            result = unit.simulate()
            unit.data = result

    def summary(self):
        print(f"\nFlowsheet: {self.name}")
        print("=" * 40)
        for unit in self.equipment:
            print(f"{unit.name} ({unit.__class__.__name__})")
            if hasattr(unit, "data"):
                for k, v in unit.data.items():
                    print(f"  {k}: {v}")
            print("-" * 30)
