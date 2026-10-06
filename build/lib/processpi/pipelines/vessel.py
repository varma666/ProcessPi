# processpi/pipelines/vessel.py

class Vessel:
    """
    Vessel represents a storage or process vessel in a fluid network.

    It can have one or more inlet and outlet connections, allowing it to
    serve as a hub for fluid flow within a pipeline system.
    """
    def __init__(self, name: str, volume: float = 0.0, pressure: float = 0.0, temperature: float = 0.0):
        """
        Initializes a Vessel object.

        Args:
            name (str): The unique identifier for the vessel.
            volume (float, optional): The maximum capacity of the vessel in cubic meters (m³).
                                      Defaults to 0.0.
            pressure (float, optional): The internal pressure of the vessel in bar.
                                        Defaults to 0.0.
            temperature (float, optional): The internal temperature of the vessel in degrees Celsius (°C).
                                           Defaults to 0.0.
        """
        self.name = name
        self.volume = volume
        self.pressure = pressure
        self.temperature = temperature
        self.inlet_nodes = []
        self.outlet_nodes = []

    def add_inlet(self, node):
        """
        Attaches a new inlet node to the vessel.

        Args:
            node: The node object (e.g., from a Pipe or Pump) that feeds into the vessel.
        """
        self.inlet_nodes.append(node)

    def add_outlet(self, node):
        """
        Attaches a new outlet node to the vessel.

        Args:
            node: The node object (e.g., from a Pipe or Valve) that the vessel feeds into.
        """
        self.outlet_nodes.append(node)

    def __repr__(self):
        """
        Returns a developer-friendly string representation of the Vessel.
        """
        return f"Vessel(name='{self.name}', volume={self.volume} m³, pressure={self.pressure} bar, temperature={self.temperature}°C)"
