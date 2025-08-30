# processpi/pipelines/network.py

from __future__ import annotations
from typing import List, Dict, Union, Optional, Any
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle

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
    # ---------------- Utility: Get all pipes in the network ----------------
    def get_all_pipes(self) -> list[Pipe]:
        """
        Returns a flat list of all Pipe objects in this network, including nested subnetworks.

        Returns:
            list[Pipe]: List of Pipe objects found in the network.
        """
        pipes = []

        for element in self.elements:
            if isinstance(element, Pipe):
                pipes.append(element)
            elif isinstance(element, PipelineNetwork):
                # Recursively get pipes from sub-networks
                pipes.extend(element.get_all_pipes())

        return pipes

    def visualize_network(self, figsize=(24, 16), base_dx=2.0, autoscale=True):
        """
        Fully recursive P&ID-style visualization with series/parallel blocks labeled.
        Features:
        - Handles nested subnetworks
        - Series flows left→right, parallel stacked vertically
        - Parallel merges and flow arrows
        - Node elevations
        - Color-coded components
        - Automatic inlets/outlets
        - Dynamic spacing and auto-scaled fonts/nodes
        - Shaded boxes with subnetwork names and connection types
        """
        G = nx.DiGraph()
        edge_colors = []

        component_colors = {
            "Pipe": "skyblue",
            "Pump": "green",
            "Fitting": "orange",
            "Vessel": "purple",
            "Equipment": "red",
            "merge": "gray"
        }

        block_colors = {
            "series": "#e0f7fa",
            "parallel": "#fff3e0"
        }

        block_labels = []  # Store subnetwork labels (x, y, width, height, text)

        # ---------------- Recursive edge collection ----------------
        def add_edges_recursive(elements):
            for elem in elements:
                if isinstance(elem, Pipe):
                    G.add_edge(elem.start_node.name, elem.end_node.name, label="Pipe")
                    edge_colors.append(component_colors["Pipe"])
                elif isinstance(elem, Pump):
                    G.add_edge(elem.start_node.name, elem.end_node.name, label="Pump")
                    edge_colors.append(component_colors["Pump"])
                elif isinstance(elem, Fitting):
                    G.add_edge(elem.node.name, elem.node.name, label=elem.fitting_type)
                    edge_colors.append(component_colors["Fitting"])
                elif isinstance(elem, (Vessel, Equipment)):
                    in_nodes = getattr(elem, "inlet_nodes", [])
                    out_nodes = getattr(elem, "outlet_nodes", [])
                    for in_node in in_nodes:
                        for out_node in out_nodes:
                            G.add_edge(
                                in_node.name,
                                out_node.name,
                                label=getattr(elem, "name", elem.__class__.__name__)
                            )
                            edge_colors.append(component_colors.get(elem.__class__.__name__, "gray"))
                elif isinstance(elem, PipelineNetwork):
                    add_edges_recursive(elem.elements)

        add_edges_recursive(self.elements)

        # ---------------- Detect network inlets and outlets ----------------
        all_nodes = set(G.nodes)
        all_targets = {target for _, target in G.edges}
        all_sources = {source for source, _ in G.edges}

        inlets = list(all_sources - all_targets)
        outlets = list(all_targets - all_sources)

        # ---------------- Compute depth ----------------
        def compute_depth(node, visited=None):
            if visited is None:
                visited = set()
            if node in visited:
                return 0
            visited.add(node)
            children = list(G.successors(node))
            if not children:
                return 1
            return 1 + max(compute_depth(child, visited) for child in children)

        network_depth = max((compute_depth(node) for node in inlets), default=1)
        dx_scaled = base_dx * max(1.0, network_depth / 5.0)

        # ---------------- Recursive layout with block tracking ----------------
        block_rects = []
        def recursive_layout(node, x=0, y=0, dx=dx_scaled, pos=None, visited=None, depth=0, parent_block=None, current_network=None):
            if pos is None:
                pos = {}
            if visited is None:
                visited = set()
            if current_network is None:
                current_network = self

            if node in visited:
                return pos
            pos[node] = (x, y)
            visited.add(node)

            # Handle series/parallel subnetwork
            children = list(G.successors(node))
            n = len(children)
            if n == 0:
                return pos

            # Vertical spacing
            dy = max(1.5, n)
            dx_dynamic = dx * (1 + depth * 0.3)

            # Track series/parallel blocks
            if n == 1:
                pos = recursive_layout(children[0], x + dx_dynamic, y, dx, pos, visited, depth + 1, parent_block, current_network)
            else:
                # Parallel branches split
                start_y = y + dy * (n - 1) / 2
                merge_y = y
                merge_node = f"{node}_merge_{depth}"
                G.add_node(merge_node, elevation=0)
                for i, child in enumerate(children):
                    child_y = start_y - i * dy
                    pos = recursive_layout(child, x + dx_dynamic, child_y, dx, pos, visited, depth + 1, parent_block, current_network)
                    # Connect leaf nodes to merge
                    branch_leaves = [n for n in G.successors(child) if G.out_degree(n) == 0]
                    for leaf in branch_leaves:
                        G.add_edge(leaf, merge_node, label="merge")
                        edge_colors.append(component_colors["merge"])
                pos[merge_node] = (x + dx_dynamic + dx, merge_y)
                # Save parallel block rectangle
                min_y = min(pos[c][1] for c in children)
                max_y = max(pos[c][1] for c in children)
                block_rects.append((x, min_y - 0.5, dx_dynamic + dx, max_y - min_y + 1, "parallel"))
                # Add label
                block_labels.append((x + 0.1, min_y + (max_y - min_y)/2, current_network.name, current_network.connection_type))

            return pos

        root_node = inlets[0] if inlets else list(G.nodes)[0]
        pos = recursive_layout(root_node)

        # ---------------- Auto-scale ----------------
        n_nodes = len(G.nodes)
        node_size = 1200
        font_size = 10
        if autoscale:
            scale_factor = max(0.3, min(1.0, 10.0 / (n_nodes ** 0.5)))
            node_size *= scale_factor
            font_size *= scale_factor

        # ---------------- Plot ----------------
        plt.figure(figsize=figsize)

        ax = plt.gca()
        # Draw shaded blocks
        for x0, y0, w, h, block_type in block_rects:
            rect = Rectangle((x0 - 0.5, y0 - 0.5), w, h, facecolor=block_colors.get(block_type, "#f0f0f0"),
                             edgecolor="black", alpha=0.2, zorder=0)
            ax.add_patch(rect)

        # Draw block labels (subnetwork name and connection type)
        for lx, ly, name, ctype in block_labels:
            ax.text(lx + 0.1, ly, f"{name}\n({ctype})", fontsize=font_size, fontweight="bold", va="center", ha="left", zorder=5)

        nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color="lightblue", zorder=2)
        labels = {n: f"{n}\n({d.get('elevation', 0)} m)" for n, d in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=font_size, font_weight="bold", zorder=3)
        nx.draw_networkx_edges(
            G, pos, arrows=True, arrowsize=20 * (font_size / 10), arrowstyle='-|>',
            edge_color=edge_colors, width=2, zorder=1
        )
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=font_size * 0.9, zorder=3)
        plt.title(f"P&ID-Style Pipeline Network: {self.name}", fontsize=font_size * 1.5)
        plt.axis("off")
        plt.show()
