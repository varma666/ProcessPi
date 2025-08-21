# processpi/pipelines/vessel.py

class Vessel:
    """
    Vessel represents a storage or process vessel in the pipeline network.
    It can have one or multiple inlet and outlet connections.
    """
    def __init__(self, name: str, volume: float = 0.0, pressure: float = 0.0, temperature: float = 0.0):
        """
        Initialize a Vessel.
        
        Args:
            name (str): Name of the vessel.
            volume (float): Vessel capacity (m³), optional.
            pressure (float): Internal pressure (bar), optional.
            temperature (float): Internal temperature (°C), optional.
        """
        self.name = name
        self.volume = volume
        self.pressure = pressure
        self.temperature = temperature
        self.inlet_nodes = []
        self.outlet_nodes = []

    def add_inlet(self, node):
        """Attach an inlet node to the vessel."""
        self.inlet_nodes.append(node)

    def add_outlet(self, node):
        """Attach an outlet node to the vessel."""
        self.outlet_nodes.append(node)

    def __repr__(self):
        return f"Vessel({self.name}, Volume={self.volume} m³, P={self.pressure} bar, T={self.temperature}°C)"
