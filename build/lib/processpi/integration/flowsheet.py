# processpi/flowsheet.py

from collections import defaultdict, deque
from typing import Dict, List, Optional, Union

from ..equipment.base import Equipment
from ..streams.energy import EnergyStream
from ..streams.material import MaterialStream


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
        # Auto-register EnergyStream if present
        if hasattr(unit, "energy_stream") and unit.energy_stream is not None:
            if unit.energy_stream not in self.energy_streams:
                self.energy_streams.append(unit.energy_stream)

    def add_material_stream(self, stream: MaterialStream):
        self.material_streams.append(stream)

    def add_energy_stream(self, stream: EnergyStream):
        self.energy_streams.append(stream)

    def _ensure_unit_registered(self, unit: Equipment) -> None:
        if unit not in self.equipment:
            self.add_equipment(unit)

    def _ensure_stream_registered(self, stream: Union[MaterialStream, EnergyStream]) -> None:
        if isinstance(stream, MaterialStream) and stream not in self.material_streams:
            self.add_material_stream(stream)
        if isinstance(stream, EnergyStream) and stream not in self.energy_streams:
            self.add_energy_stream(stream)

    # --------------------------
    # Connections
    # --------------------------
    def connect(self, *args):
        """
        Connect stream between units using named ports.

        Preferred signature:
            connect(stream, from_unit, from_port, to_unit, to_port)

        Backward-compatible signature:
            connect(stream, to_unit, to_port)
        """
        if len(args) == 5:
            stream, from_unit, from_port, to_unit, to_port = args
        elif len(args) == 3:
            stream, to_unit, to_port = args
            from_unit = None
            from_port = None
        else:
            raise TypeError("connect expects either 3 args or 5 args.")

        if not isinstance(stream, (MaterialStream, EnergyStream)):
            raise TypeError("First argument must be MaterialStream or EnergyStream.")
        if not isinstance(to_unit, Equipment):
            raise TypeError("Destination unit must be an Equipment instance.")
        if from_unit is not None and not isinstance(from_unit, Equipment):
            raise TypeError("Source unit must be an Equipment instance.")

        self._ensure_stream_registered(stream)
        self._ensure_unit_registered(to_unit)
        if from_unit is not None:
            self._ensure_unit_registered(from_unit)

        # Validate destination inlet
        if to_port not in to_unit.inlets:
            raise ValueError(f"{to_unit.name}: inlet port '{to_port}' does not exist.")
        if to_unit.inlets[to_port] is not None and to_unit.inlets[to_port] is not stream:
            raise ValueError(f"{to_unit.name}: inlet port '{to_port}' already has a stream.")

        if from_unit is not None:
            # Validate source outlet
            if from_port not in from_unit.outlets:
                raise ValueError(f"{from_unit.name}: outlet port '{from_port}' does not exist.")
            if from_unit.outlets[from_port] is not None and from_unit.outlets[from_port] is not stream:
                raise ValueError(f"{from_unit.name}: outlet port '{from_port}' already has a stream.")

            from_unit.connect_outlet(from_port, stream) if from_unit.outlets[from_port] is None else None

        to_unit.connect_inlet(to_port, stream) if to_unit.inlets[to_port] is None else None

        conn = {
            "stream": stream,
            "from_unit": from_unit,
            "from_port": from_port,
            "to_unit": to_unit,
            "to_port": to_port,
        }
        if conn not in self.connections:
            self.connections.append(conn)

    # --------------------------
    # Dependency graph
    # --------------------------
    def _build_dependency_graph(self):
        """Build graph of unit dependencies based on connections"""
        graph = defaultdict(list)
        indegree = {u.name: 0 for u in self.equipment}

        for conn in self.connections:
            src: Optional[Equipment] = conn.get("from_unit")  # type: ignore[assignment]
            dst: Equipment = conn["to_unit"]  # type: ignore[assignment]
            if src is not None and src is not dst:
                graph[src.name].append(dst.name)
                indegree[dst.name] += 1

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
        """Topologically sorted flowsheet solve."""
        order = self._topological_order()
        name_to_unit = {u.name: u for u in self.equipment}

        for uname in order:
            unit = name_to_unit[uname]
            print(f"➡️ Running {unit.name} ({unit.__class__.__name__})")
            result = unit.simulate()
            unit.data = result

    def solve_sequential(self):
        """Simple sequential solve in registration order."""
        for unit in self.equipment:
            print(f"➡️ Running {unit.name} ({unit.__class__.__name__})")
            unit.data = unit.simulate()

    def summary(self):
        print(f"\nFlowsheet: {self.name}")
        print("=" * 40)
        for unit in self.equipment:
            print(f"{unit.name} ({unit.__class__.__name__})")
            if hasattr(unit, "data"):
                for k, v in unit.data.items():
                    print(f"  {k}: {v}")
            print("-" * 30)
