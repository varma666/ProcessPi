
class Equipment:
    """
    Generic inline process equipment with inlet, outlet, and pressure drop.
    Can represent filters, heat exchangers, valves, or other unit operations.
    """
    def __init__(self, name: str, pressure_drop: float = 0.0, description: str = ""):
        """
        Initialize Equipment.

        Args:
            name (str): Equipment name.
            pressure_drop (float): Pressure drop across equipment (bar).
            description (str): Optional description (e.g., 'Heat Exchanger', 'Filter').
        """
        self.name = name
        self.pressure_drop = pressure_drop
        self.description = description
        self.inlet_nodes = []
        self.outlet_nodes = []

    def add_inlet(self, node):
        """Attach an inlet node to the equipment."""
        self.inlet_nodes.append(node)

    def add_outlet(self, node):
        """Attach an outlet node to the equipment."""
        self.outlet_nodes.append(node)

    def __repr__(self):
        return (f"Equipment({self.name}, ΔP={self.pressure_drop} bar, "
                f"Desc='{self.description}')")
