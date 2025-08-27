# processpi/pipelines/network.py

from __future__ import annotations
from typing import List, Dict, Union, Optional, Any

from .pipes import Pipe
from .fittings import Fitting
from .vessel import Vessel
from .pumps import Pump
from .equipment import Equipment
from ..units import *

class Node:
    """
    Represents a connection point, junction, or endpoint in a pipeline network.

    Nodes have a name for identification and an elevation for calculating
    static head differences in the system.
    """
    def __init__(self, name: str, elevation: float = 0.0):
        """
        Initializes a Node instance.

        Args:
            name (str): A unique identifier for the node.
            elevation (float, optional): The elevation of the node in meters.
                                         Used in pressure calculations. Defaults to 0.0.
        """
        self.name: str = name
        self.elevation: float = elevation
        self.pressure: Optional[Pressure] = None
        self.flow_rate: Optional[VolumetricFlowRate] = None
        self.connected_components: List[Any] = []

    def __repr__(self):
        return f"Node(name='{self.name}', elevation={self.elevation} m)"


# A branch in a parallel block can be either a PipelineNetwork or a single element
Branch = Union["PipelineNetwork", Pipe, Fitting, Pump, Vessel, Equipment]


class PipelineNetwork:
    """
    A framework for defining a process pipeline network.

    This class provides a dual-purpose structure:
    1. A **node-and-edge graph** for general network problems.
    2. A **composable series/parallel block model** for easier, hierarchical
       construction and calculation, compatible with a `PipelineEngine`.
    """

    # ---------------- Init ----------------
    def __init__(self, name: str, connection_type: Optional[str] = "series"):
        """
        Initializes a PipelineNetwork instance.

        Args:
            name (str): The name of the network.
            connection_type (Optional[str], optional): The connection type for
                                                       the elements within this block.
                                                       Can be "series" or "parallel".
                                                       Defaults to "series".
        """
        if connection_type not in (None, "series", "parallel"):
            raise ValueError("`connection_type` must be 'series' or 'parallel' (or None which defaults to 'series').")
        
        self.name: str = name
        self.nodes: Dict[str, Node] = {}
        self.elements: List[Branch] = []
        # The primary mode of operation for this network block.
        self.connection_type: str = connection_type or "series"

    # ---------------- Convenience constructors (engine-friendly) -------------
    @staticmethod
    def series(name: str, *elements: Branch) -> "PipelineNetwork":
        """
        Class method to create a series block pre-populated with elements.

        Args:
            name (str): The name for the series network.
            *elements (Branch): A variable number of elements (Pipes, Fittings,
                                or other networks) to be added in series.

        Returns:
            PipelineNetwork: A new PipelineNetwork instance configured for series flow.
        """
        net = PipelineNetwork(name=name, connection_type="series")
        net.elements.extend(elements)
        return net

    @staticmethod
    def parallel(name: str, *branches: Branch) -> "PipelineNetwork":
        """
        Class method to create a parallel block with pre-defined branches.

        Args:
            name (str): The name for the parallel network.
            *branches (Branch): A variable number of branches (elements or child
                                networks) that exist in parallel.

        Returns:
            PipelineNetwork: A new PipelineNetwork instance configured for parallel flow.
        """
        net = PipelineNetwork(name=name, connection_type="parallel")
        net.elements.extend(branches)
        return net

    # ---------------- Composable builders ------------------------------------
    def add(self, *elements: Branch) -> "PipelineNetwork":
        """
        A unified method to append one or more elements to the current network block.
        This provides a more fluent and readable interface for building.

        Args:
            *elements (Branch): One or more elements to add.

        Returns:
            PipelineNetwork: The current network instance, allowing for method chaining.
        """
        self.elements.extend(elements)
        return self

    def add_series(self, *elements: Branch) -> "PipelineNetwork":
        """
        Adds a series group to the network.
        
        If the current network is a series block, it appends the new elements
        directly. If it is a parallel block, it wraps the new elements in a
        child series network, which is then added as a branch. This preserves
        the correct hierarchical structure.

        Args:
            *elements (Branch): The elements to add to the series group.

        Returns:
            PipelineNetwork: The current network instance for chaining.
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
        Adds a parallel group to the network.

        If the current network is a parallel block, it appends the new branches
        directly. If it is a series block, it wraps the new branches in a
        child parallel network, which is then added as a single element.

        Args:
            *branches (Branch): The branches (elements or networks) to add to the parallel group.

        Returns:
            PipelineNetwork: The current network instance for chaining.
        """
        if self.connection_type == "parallel":
            self.elements.extend(branches)
            return self
        
        par_child = PipelineNetwork(name=f"{self.name}-parallel-{len(self.elements)+1}", connection_type="parallel")
        par_child.elements.extend(branches)
        self.elements.append(par_child)
        return self

    # ---------------- Node & Edge Management (Graph-based construction) ------
    def add_node(self, name: str, elevation: float = 0.0) -> Node:
        """
        Adds a new node (junction) to the network's internal node dictionary.

        Args:
            name (str): The unique name of the node.
            elevation (float, optional): The elevation in meters. Defaults to 0.0.

        Returns:
            Node: The newly created Node object.

        Raises:
            ValueError: If a node with the given name already exists.
        """
        if name in self.nodes:
            raise ValueError(f"Node '{name}' already exists in the network.")
            
        node = Node(name, elevation)
        self.nodes[name] = node
        return node

    def get_node(self, name: str) -> Node:
        """
        Fetches an existing node by name from the network's node dictionary.

        Args:
            name (str): The name of the node to retrieve.

        Returns:
            Node: The found Node object.

        Raises:
            KeyError: If the node does not exist in the network.
        """
        if name not in self.nodes:
            raise KeyError(f"Node '{name}' does not exist in the network.")
            
        return self.nodes[name]

    def add_edge(self, component: Union[Pipe, Pump, Vessel, Equipment], start_node: str, end_node: str):
        """
        Adds a connection (an edge) between two existing nodes using a component.

        This method strictly links components that have a defined inlet and outlet
        to the network's nodes. It also automatically adds the component to the
        network's `elements` list.

        Args:
            component (Union[Pipe, Pump, Vessel, Equipment]): The component to connect.
            start_node (str): The name of the inlet node.
            end_node (str): The name of the outlet node.

        Raises:
            ValueError: If either the start or end node is not found, or if a
                        self-loop (start=end) is attempted.
            TypeError: If the component type is not supported for edge creation.
        """
        if start_node not in self.nodes:
            raise ValueError(f"Start node '{start_node}' not found in network.")
        if end_node not in self.nodes:
            raise ValueError(f"End node '{end_node}' not found in network.")
        if start_node == end_node:
            raise ValueError(f"Cannot create a self-loop on node '{start_node}'.")

        # Assign nodes based on component type.
        if isinstance(component, (Pipe, Pump)):
            component.start_node = self.nodes[start_node]
            component.end_node = self.nodes[end_node]
        elif isinstance(component, (Vessel, Equipment)):
            # These components have their own methods for adding inlet/outlet nodes
            component.add_inlet(self.nodes[start_node])
            component.add_outlet(self.nodes[end_node])
        else:
            raise TypeError(f"Unsupported component type '{type(component).__name__}' for edge creation.")
        
        self.elements.append(component)

    def add_fitting(self, fitting: Fitting, at_node: str):
        """
        Adds a fitting to a specific node within the network.

        Fittings are considered zero-length elements, so they are associated
        with a single node rather than an edge.

        Args:
            fitting (Fitting): The fitting object to add.
            at_node (str): The name of the node where the fitting is located.

        Raises:
            ValueError: If the specified node does not exist.
        """
        if at_node not in self.nodes:
            raise ValueError(f"Node '{at_node}' must exist in the network.")
        
        fitting.node = self.nodes[at_node]
        self.elements.append(fitting)

    def add_subnetwork(self, subnetwork: "PipelineNetwork"):
        """
        Adds an existing PipelineNetwork instance as a child element.
        This provides compatibility with code that constructs subnetworks separately.

        Args:
            subnetwork (PipelineNetwork): The pre-built subnetwork to add.

        Raises:
            ValueError: If the subnetwork is the same as the parent network.
        """
        if subnetwork is self:
            raise ValueError("Cannot add the network as a subnetwork of itself.")
            
        self.elements.append(subnetwork)

    # ---------------- Validation ----------------
    def validate(self):
        """
        Performs a comprehensive check for common network errors.
        This includes checking for unconnected nodes and ensuring all elements
        have required properties.
        
        Raises:
            ValueError: If any validation errors are found. The exception message
                        will list all detected issues.
        """
        errors = []

        # 1. Check for unconnected nodes (graph validation)
        connected_node_names = set()
        for elem in self.elements:
            if isinstance(elem, (Pipe, Pump)):
                if getattr(elem, "start_node", None) and getattr(elem, "end_node", None):
                    connected_node_names.add(elem.start_node.name)
                    connected_node_names.add(elem.end_node.name)
            elif isinstance(elem, (Vessel, Equipment)):
                for n in getattr(elem, "inlet_nodes", []):
                    connected_node_names.add(n.name)
                for n in getattr(elem, "outlet_nodes", []):
                    connected_node_names.add(n.name)
            elif isinstance(elem, Fitting):
                if getattr(elem, "node", None):
                    connected_node_names.add(elem.node.name)
            elif isinstance(elem, PipelineNetwork):
                # Recurse into child blocks for validation
                try:
                    elem.validate()
                except ValueError as e:
                    errors.append(f"In subnetwork '{elem.name}': {e}")

        for node_name in self.nodes:
            if node_name not in connected_node_names:
                errors.append(f"Node '{node_name}' is not connected to any component.")

        # 2. Check for component-specific validation rules
        for elem in self.elements:
            # Skip validation for child networks, as their errors were already collected
            if isinstance(elem, PipelineNetwork):
                continue
            
            if isinstance(elem, Fitting):
                if not isinstance(getattr(elem, "diameter", None), Diameter):
                    errors.append(f"Fitting '{elem.fitting_type}' requires 'diameter' to be a `Diameter` object.")
                if elem.total_K() is None and elem.equivalent_length() is None:
                    errors.append(f"Fitting '{elem.fitting_type}' has no 'K' or 'L/D' data in standards.")
            
            if isinstance(elem, Pump):
                head = getattr(elem, "head", 0)
                inlet_p = getattr(elem, "inlet_pressure", None)
                outlet_p = getattr(elem, "outlet_pressure", None)
                if (head is None or head == 0) and (not inlet_p or not outlet_p):
                    errors.append(f"Pump '{getattr(elem, 'name', 'pump')}' requires either a non-zero `head` or defined `inlet_pressure` and `outlet_pressure`.")
            
            if isinstance(elem, Equipment):
                if getattr(elem, "pressure_drop", None) is None:
                    errors.append(f"Equipment '{getattr(elem, 'name', 'equipment')}' requires a non-None `pressure_drop` value (bar).")

        if errors:
            raise ValueError(f"Network validation failed:\n" + "\n".join(errors))
            
        return True

    # ---------------- Description & ASCII Schematic ----------------
    def describe(self, level: int = 0) -> str:
        """
        Returns a detailed, hierarchical string representation of the network.
        
        Args:
            level (int): The current indentation level for nested networks.
        
        Returns:
            str: A multi-line string describing the network's structure.
        """
        indent = "  " * level
        desc = f"{indent}Network: {self.name} (connection: {self.connection_type})\n"
        
        # Add a section for nodes within this network block
        if self.nodes:
            desc += f"{indent}  Nodes:\n"
            for node in self.nodes.values():
                desc += f"{indent}    {node}\n"

        desc += f"{indent}  Elements:\n"
        if not self.elements:
            desc += f"{indent}    (none)\n"
            
        for element in self.elements:
            if isinstance(element, Pipe):
                desc += (
                    f"{indent}    Pipe: {getattr(element, 'nominal_diameter', 'NA')} mm, "
                    f"L={getattr(element, 'length', 'NA')} m, "
                    f"from {element.start_node.name} → {element.end_node.name}\n"
                )
            elif isinstance(element, Pump):
                desc += (
                    f"{indent}    Pump: {getattr(element, 'pump_type', 'Generic')}, "
                    f"from {element.start_node.name} → {element.end_node.name}\n"
                )
            elif isinstance(element, Fitting):
                where = getattr(element, 'node', None)
                at = where.name if where else "unknown"
                desc += f"{indent}    Fitting: {getattr(element, 'fitting_type', 'Fitting')} at {at}\n"
            elif isinstance(element, Vessel):
                inlets = ", ".join([n.name for n in getattr(element, "inlet_nodes", [])])
                outlets = ", ".join([n.name for n in getattr(element, "outlet_nodes", [])])
                desc += f"{indent}    Vessel: {getattr(element, 'name', 'Vessel')}, In: {inlets}, Out: {outlets}\n"
            elif isinstance(element, Equipment):
                inlets = ", ".join([n.name for n in getattr(element, "inlet_nodes", [])])
                outlets = ", ".join([n.name for n in getattr(element, "outlet_nodes", [])])
                desc += f"{indent}    Equipment: {getattr(element, 'name', 'Equipment')}, In: {inlets}, Out: {outlets}\n"
            elif isinstance(element, PipelineNetwork):
                desc += element.describe(level + 1)
        
        return desc

    def schematic(self) -> str:
        """
        Generates an ASCII schematic representation of the network's hierarchical
        structure.
        
        Returns:
            str: A multi-line string visual representation of the network.
        """
        return "\n".join(self._schematic_lines())

    def _schematic_lines(self, prefix: str = "") -> List[str]:
        """Recursive helper method for generating schematic lines."""
        lines: List[str] = []
        header = f"{prefix}└─{self.name} [{self.connection_type}]" if prefix else f"{self.name} [{self.connection_type}]"
        lines.append(header)
        
        child_prefix_base = prefix + "  "
        if self.connection_type == "series":
            for i, el in enumerate(self.elements, start=1):
                child_prefix = child_prefix_base + "│ " if i < len(self.elements) else child_prefix_base + "  "
                
                if isinstance(el, PipelineNetwork):
                    lines.extend(el._schematic_lines(child_prefix))
                else:
                    label = getattr(el, "name", el.__class__.__name__)
                    lines.append(f"{child_prefix}└─{i}. {label}")
        else:  # parallel
            for i, br in enumerate(self.elements, start=1):
                child_prefix = child_prefix_base + "  "
                lines.append(f"{child_prefix}┌─(branch {i})")
                
                if isinstance(br, PipelineNetwork):
                    lines.extend(br._schematic_lines(child_prefix + "│ "))
                else:
                    label = getattr(br, "name", br.__class__.__name__)
                    lines.append(f"{child_prefix}│   └─ {label}")
                
        return lines

    # ---------------- Python niceties ----------------------------------------
    def __repr__(self) -> str:
        return f"PipelineNetwork(name='{self.name}', type='{self.connection_type}', elements={len(self.elements)})"
