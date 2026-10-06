# processpi/equipment.py

from typing import List, Any

class Equipment:
    """
    Represents a generic piece of inline process equipment within a fluid flow
    network, such as a heat exchanger, filter, or control valve.

    This class models the equipment as a component that causes a fixed
    pressure drop. It also includes attributes to define its connections
    within a network.
    """
    def __init__(self, name: str, pressure_drop: float = 0.0, description: str = ""):
        """
        Initializes an Equipment instance.

        Args:
            name (str): A unique name for the equipment (e.g., 'HX-101', 'Valve-2A').
            pressure_drop (float, optional): The pressure drop across the equipment in bar.
                                             Defaults to 0.0.
            description (str, optional): A brief description of the equipment type
                                         (e.g., 'Shell & Tube Heat Exchanger', 'Filter').
        """
        # A human-readable name for the equipment.
        self.name: str = name
        
        # The specified pressure drop, assumed to be in bar.
        self.pressure_drop: float = pressure_drop
        
        # An optional description for more context.
        self.description: str = description
        
        # Lists to hold references to connected nodes in a pipeline network.
        # Nodes are typically abstract points representing junctions or boundaries.
        self.inlet_nodes: List[Any] = []
        self.outlet_nodes: List[Any] = []

    def add_inlet(self, node: Any) -> None:
        """
        Adds a node to the list of inlet connections.

        Args:
            node (Any): The node object to connect as an inlet.
        """
        self.inlet_nodes.append(node)

    def add_outlet(self, node: Any) -> None:
        """
        Adds a node to the list of outlet connections.

        Args:
            node (Any): The node object to connect as an outlet.
        """
        self.outlet_nodes.append(node)

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the object.

        Returns:
            str: A string showing the class, name, pressure drop, and description.
        """
        return (f"Equipment(name='{self.name}', pressure_drop={self.pressure_drop} bar, "
                f"description='{self.description}')")
