from __future__ import annotations
from typing import List, Dict, Union, Optional, Any

from .pipes import Pipe
from .fittings import Fitting
from .vessel import Vessel
from .pump import Pump
from .equipment import Equipment


class Node:
    """Node represents a junction or endpoint in the pipeline network."""
    def __init__(self, name: str, elevation: float = 0.0):
        self.name = name
        self.elevation = elevation

    def __repr__(self):
        return f"Node({self.name}, elevation={self.elevation})"


# A branch in a parallel block can be either a PipelineNetwork or a single element
Branch = Union["PipelineNetwork", Pipe, Fitting, Pump, Vessel, Equipment]


class PipelineNetwork:
    """
    Framework for defining a process pipeline network consisting of pipes,
    fittings, pumps, vessels, equipment, and sub-networks.

    This version supports both node/edge construction AND composable
    series/parallel blocks compatible with the PipelineEngine:
      - connection_type: "series" (default) or "parallel"
      - elements: a list of elements or child PipelineNetwork objects
    """

    # ---------------- Init ----------------
    def __init__(self, name: str, connection_type: Optional[str] = "series"):
        if connection_type not in (None, "series", "parallel"):
            raise ValueError("connection_type must be 'series' or 'parallel' (or None which defaults to 'series').")
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.elements: List[Branch] = []
        self.connection_type: str = connection_type or "series"

    # ---------------- Convenience constructors (engine-friendly) -------------
    @staticmethod
    def series(name: str, *elements: Branch) -> "PipelineNetwork":
        """Create a series block populated with elements."""
        net = PipelineNetwork(name=name, connection_type="series")
        net.elements.extend(elements)
        return net

    @staticmethod
    def parallel(name: str, *branches: Branch) -> "PipelineNetwork":
        """Create a parallel block populated with branch elements or child networks."""
        net = PipelineNetwork(name=name, connection_type="parallel")
        net.elements.extend(branches)
        return net

    # ---------------- Composable builders ------------------------------------
    def add(self, *elements: Branch) -> "PipelineNetwork":
        """Append one or more elements to the current block (series or parallel)."""
        self.elements.extend(elements)
        return self

    def add_series(self, *elements: Branch) -> "PipelineNetwork":
        """
        Add a series group. If the current block is series, append directly.
        If current block is parallel, wrap as a child series network (a branch).
        """
        if self.connection_type == "series":
            self.elements.extend(elements)
            return self
        series_child = PipelineNetwork(name=f"{self.name}-series-{len(self.elements)+1}", connection_type="series")
        series_child.elements.extend(elements)
        self.elements.append(series_child)
        return self

    def add_parallel(self, *branches: Branch) -> "PipelineNetwork":
        """
        Add a parallel group. If current block is parallel, append as new branches.
        If current block is series, wrap as a child parallel network (one element).
        """
        if self.connection_type == "parallel":
            self.elements.extend(branches)
            return self
        par_child = PipelineNetwork(name=f"{self.name}-parallel-{len(self.elements)+1}", connection_type="parallel")
        par_child.elements.extend(branches)
        self.elements.append(par_child)
        return self

    # ---------------- Node Management ----------------
    def add_node(self, name: str, elevation: float = 0.0) -> Node:
        """Add a node (junction) to the network."""
        if name in self.nodes:
            raise ValueError(f"Node '{name}' already exists in the network.")
        node = Node(name, elevation)
        self.nodes[name] = node
        return node

    def get_node(self, name: str) -> Node:
        """Fetch an existing node by name."""
        if name not in self.nodes:
            raise KeyError(f"Node '{name}' does not exist in the network.")
        return self.nodes[name]

    # ---------------- Edge Management ----------------
    def add_edge(self, component: Union[Pipe, Pump, Vessel, Equipment], start_node: str, end_node: str = None):
        """
        Add a connection (edge) between nodes with strict validation.
        Edges added here are automatically appended to this block's elements.
        """
        if start_node not in self.nodes:
            raise ValueError(f"Start node '{start_node}' not found in network.")

        # Prevent start=end self-loops
        if end_node and start_node == end_node:
            raise ValueError(f"Cannot create self-loop on node '{start_node}'.")

        if isinstance(component, (Pipe, Pump)):
            if not end_node or end_node not in self.nodes:
                raise ValueError(f"End node '{end_node}' not found in network.")
            component.start_node = self.nodes[start_node]
            component.end_node = self.nodes[end_node]

        elif isinstance(component, (Vessel, Equipment)):
            if not end_node or end_node not in self.nodes:
                raise ValueError(f"Outlet node '{end_node}' not found in network.")
            component.add_inlet(self.nodes[start_node])
            component.add_outlet(self.nodes[end_node])

        else:
            raise TypeError(f"Unsupported component type '{type(component).__name__}'.")

        self.elements.append(component)

    # ---------------- Element Management ----------------
    def add_fitting(self, fitting: Fitting, at_node: str):
        """Add a fitting at a specific node."""
        if at_node not in self.nodes:
            raise ValueError(f"Node '{at_node}' must exist in the network.")
        fitting.node = self.nodes[at_node]
        self.elements.append(fitting)

    def add_subnetwork(self, subnetwork: "PipelineNetwork", connection_type: str):
        """
        Add a subnetwork (series or parallel) as a child element.
        This preserves compatibility with existing code that constructs subnetworks separately.
        """
        if connection_type not in ["series", "parallel"]:
            raise ValueError("connection_type must be 'series' or 'parallel'")
        if subnetwork is self:
            raise ValueError("Cannot add the network as a subnetwork of itself.")
        subnetwork.connection_type = connection_type
        self.elements.append(subnetwork)

    # ---------------- Validation ----------------
    def validate(self):
        """Check for common network errors and raise descriptive exceptions."""
        errors = []

        # Collect connected node names from elements in this block only
        connected = set()
        for elem in self.elements:
            if isinstance(elem, (Pipe, Pump)):
                if getattr(elem, "start_node", None) and getattr(elem, "end_node", None):
                    connected.update([elem.start_node.name, elem.end_node.name])
            elif isinstance(elem, (Vessel, Equipment)):
                for n in getattr(elem, "inlet_nodes", []) or []:
                    connected.add(n.name)
                for n in getattr(elem, "outlet_nodes", []) or []:
                    connected.add(n.name)
            elif isinstance(elem, PipelineNetwork):
                # recurse into child blocks for validation too
                try:
                    elem.validate()
                except ValueError as e:
                    errors.append(f"In subnetwork '{elem.name}': {e}")

        for node_name in self.nodes:
            if node_name not in connected:
                errors.append(f"Node '{node_name}' is not connected to any component.")

        if errors:
            raise ValueError("Network validation failed:\n" + "\n".join(errors))
        return True

    # ---------------- Description ----------------
    def describe(self, level: int = 0) -> str:
        """Return a string representation of the network hierarchy."""
        indent = "  " * level
        desc = f"{indent}Network: {self.name} (connection: {self.connection_type})\n"
        for node in self.nodes.values():
            desc += f"{indent}  Node: {node.name}, Elevation={node.elevation} m\n"
        for element in self.elements:
            if isinstance(element, Pipe):
                desc += (
                    f"{indent}  Pipe: {getattr(element, 'nominal_diameter', 'NA')} mm, "
                    f"{getattr(element, 'length', 'NA')} m, {getattr(element, 'material', 'NA')}, "
                    f"from {element.start_node.name} → {element.end_node.name}\n"
                )
            elif isinstance(element, Pump):
                desc += (
                    f"{indent}  Pump: {getattr(element, 'pump_type', 'Generic')}, "
                    f"from {element.start_node.name} → {element.end_node.name}, "
                    f"Head={getattr(element, 'head', 'NA')} m, Power={getattr(element, 'power', 'NA')} kW\n"
                )
            elif isinstance(element, Vessel):
                inlets = ", ".join([n.name for n in getattr(element, "inlet_nodes", [])])
                outlets = ", ".join([n.name for n in getattr(element, "outlet_nodes", [])])
                desc += f"{indent}  Vessel: {getattr(element, 'name', 'Vessel')}, Volume={getattr(element, 'volume', 'NA')} m³, P={getattr(element, 'pressure', 'NA')} bar, T={getattr(element, 'temperature', 'NA')}°C\n"
                desc += f"{indent}    Inlets: {inlets or '—'}\n"
                desc += f"{indent}    Outlets: {outlets or '—'}\n"
            elif isinstance(element, Equipment):
                inlets = ", ".join([n.name for n in getattr(element, "inlet_nodes", [])])
                outlets = ", ".join([n.name for n in getattr(element, "outlet_nodes", [])])
                desc += (f"{indent}  Equipment: {getattr(element, 'name', 'Equipment')}, "
                         f"ΔP={getattr(element, 'pressure_drop', 'NA')} bar, "
                         f"Type={getattr(element, 'description', 'Generic')}\n")
                desc += f"{indent}    Inlet(s): {inlets or '—'}\n"
                desc += f"{indent}    Outlet(s): {outlets or '—'}\n"
            elif isinstance(element, Fitting):
                where = getattr(element, 'node', None)
                at = where.name if where else "unknown"
                desc += f"{indent}  Fitting: {getattr(element, 'fitting_type', 'Fitting')}, at {at}\n"
            elif isinstance(element, PipelineNetwork):
                desc += element.describe(level + 1)
        return desc

    # ---------------- ASCII Schematic (engine-friendly) ----------------------
    def _schematic_lines(self, prefix: str = "") -> List[str]:
        lines: List[str] = []
        header = f"{prefix}{self.name} [{self.connection_type}]"
        lines.append(header)
        child_prefix = prefix + "  "
        if self.connection_type == "series":
            for i, el in enumerate(self.elements, start=1):
                if isinstance(el, PipelineNetwork):
                    lines.extend(el._schematic_lines(child_prefix))
                else:
                    label = getattr(el, "name", el.__class__.__name__)
                    lines.append(f"{child_prefix}{i}. {label}")
        else:  # parallel
            for i, br in enumerate(self.elements, start=1):
                if isinstance(br, PipelineNetwork):
                    lines.append(f"{child_prefix}(branch {i})")
                    lines.extend(br._schematic_lines(child_prefix + "  "))
                else:
                    label = getattr(br, "name", br.__class__.__name__)
                    lines.append(f"{child_prefix}├─(branch {i}) {label}")
        return lines

    def schematic(self, level: int = 0) -> str:
        """
        Generate ASCII schematic representation of the pipeline network.
        Kept compatible with the PipelineEngine which calls `network.schematic()`.
        """
        return "\n".join(self._schematic_lines())

    # ---------------- Python niceties ----------------------------------------
    def __repr__(self) -> str:
        return f"PipelineNetwork(name={self.name!r}, type={self.connection_type!r}, elements={len(self.elements)})"
