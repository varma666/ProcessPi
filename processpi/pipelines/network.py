from typing import List, Dict, Union, Optional
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


class PipelineNetwork:
    """
    Framework for defining a process pipeline network consisting of pipes,
    fittings, pumps, vessels, equipment, and sub-networks.
    """

    def __init__(self, name: str):
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.elements: List[Union[Pipe, Fitting, Pump, Vessel, Equipment, "PipelineNetwork"]] = []
        self.connection_type: Optional[str] = None  # 'series' or 'parallel'

    # ---------------- Node Management ----------------
    def add_node(self, name: str, elevation: float = 0.0) -> Node:
        """Add a node (junction) to the network."""
        node = Node(name, elevation)
        self.nodes[name] = node
        return node

    def get_node(self, name: str) -> Node:
        """Fetch an existing node by name."""
        return self.nodes[name]

    # ---------------- Edge Management ----------------
    def add_edge(self, component: Union[Pipe, Pump, Vessel, Equipment], start_node: str, end_node: str = None):
        """
        General-purpose method to add a connection (edge) between nodes.
        - For Pipe and Pump: requires start_node and end_node.
        - For Vessel and Equipment: requires both inlet and outlet nodes.
        """
        if start_node not in self.nodes:
            raise ValueError(f"Start node '{start_node}' not found in network.")
        if isinstance(component, (Pipe, Pump)):
            if end_node not in self.nodes:
                raise ValueError(f"End node '{end_node}' not found in network.")
            component.start_node = self.nodes[start_node]
            component.end_node = self.nodes[end_node]
        elif isinstance(component, (Vessel, Equipment)):
            if end_node not in self.nodes:
                raise ValueError(f"Outlet node '{end_node}' not found in network.")
            component.add_inlet(self.nodes[start_node])
            component.add_outlet(self.nodes[end_node])
        else:
            raise TypeError(f"Unsupported component type for add_edge: {type(component).__name__}")

        self.elements.append(component)

    # ---------------- Element Management ----------------
    def add_fitting(self, fitting: Fitting, at_node: str):
        """Add a fitting at a specific node."""
        if at_node not in self.nodes:
            raise ValueError("Node must exist in the network.")
        fitting.node = self.nodes[at_node]
        self.elements.append(fitting)

    def add_subnetwork(self, subnetwork: "PipelineNetwork", connection_type: str):
        """Add a subnetwork (series or parallel)."""
        if connection_type not in ["series", "parallel"]:
            raise ValueError("connection_type must be 'series' or 'parallel'")
        subnetwork.connection_type = connection_type
        self.elements.append(subnetwork)

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
                    f"{indent}  Pipe: {element.nominal_diameter} mm, "
                    f"{element.length} m, {element.material}, "
                    f"from {element.start_node.name} → {element.end_node.name}\n"
                )
            elif isinstance(element, Pump):
                desc += (
                    f"{indent}  Pump: {element.pump_type}, "
                    f"from {element.start_node.name} → {element.end_node.name}, "
                    f"Head={element.head} m, Power={element.power} kW\n"
                )
            elif isinstance(element, Vessel):
                inlets = ", ".join([n.name for n in element.inlet_nodes])
                outlets = ", ".join([n.name for n in element.outlet_nodes])
                desc += f"{indent}  Vessel: {element.name}, Volume={element.volume} m³, P={element.pressure} bar, T={element.temperature}°C\n"
                desc += f"{indent}    Inlets: {inlets}\n"
                desc += f"{indent}    Outlets: {outlets}\n"
            elif isinstance(element, Equipment):
                inlets = ", ".join([n.name for n in element.inlet_nodes])
                outlets = ", ".join([n.name for n in element.outlet_nodes])
                desc += (f"{indent}  Equipment: {element.name}, ΔP={element.pressure_drop} bar, "
                         f"Type={element.description or 'Generic'}\n")
                desc += f"{indent}    Inlet(s): {inlets}\n"
                desc += f"{indent}    Outlet(s): {outlets}\n"
            elif isinstance(element, Fitting):
                desc += f"{indent}  Fitting: {element.fitting_type}, at {element.node.name}\n"
            elif isinstance(element, PipelineNetwork):
                desc += element.describe(level + 1)
        return desc

    # ---------------- ASCII Schematic ----------------
    def schematic(self, level: int = 0) -> str:
        """Generate ASCII schematic representation of the pipeline network."""
        indent = "  " * level
        schematic = f"{indent}[{self.name}] ({self.connection_type or 'series'})\n"

        for element in self.elements:
            if isinstance(element, Pipe):
                schematic += f"{indent}  {element.start_node.name} --({element.nominal_diameter}mm)--> {element.end_node.name}\n"
            elif isinstance(element, Pump):
                schematic += f"{indent}  {element.start_node.name} ==[Pump:{element.pump_type}]==> {element.end_node.name}\n"
            elif isinstance(element, Vessel):
                for inlet in element.inlet_nodes:
                    schematic += f"{indent}  {inlet.name} --> [Vessel: {element.name}]\n"
                for outlet in element.outlet_nodes:
                    schematic += f"{indent}  [Vessel: {element.name}] --> {outlet.name}\n"
            elif isinstance(element, Equipment):
                for inlet in element.inlet_nodes:
                    schematic += f"{indent}  {inlet.name} --> [Equipment: {element.name}]\n"
                for outlet in element.outlet_nodes:
                    schematic += f"{indent}  [Equipment: {element.name}] --> {outlet.name}\n"
            elif isinstance(element, Fitting):
                schematic += f"{indent}  [Fitting: {element.fitting_type} at {element.node.name}]\n"
            elif isinstance(element, PipelineNetwork):
                if element.connection_type == "parallel":
                    schematic += f"{indent}  ┌── Parallel ──┐\n"
                    schematic += element.schematic(level + 2)
                    schematic += f"{indent}  └──────────────┘\n"
                else:
                    schematic += element.schematic(level + 1)

        return schematic
