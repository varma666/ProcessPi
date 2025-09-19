from ..units import Power, Energy

class EnergyStream:
    """
    Represents an energy stream (heat or work transfer).
    Can bind to a MaterialStream to log duties automatically.
    """

    def __init__(self, name: str, duty: Power = None, energy: Energy = None):
        self.name = name
        self.duty = duty   # instantaneous transfer rate (kW)
        self.energy = energy  # accumulated energy (kJ), optional
        self.bound_streams = []  # MaterialStreams connected
        self.log = []  # history of duties per simulation

    def bind(self, stream: "MaterialStream"):
        """Bind this EnergyStream to a MaterialStream (inlet or outlet)."""
        if stream not in self.bound_streams:
            self.bound_streams.append(stream)

    def record(self, duty: Power, equipment: str):
        """
        Record an energy duty event, tagged with equipment name.
        """
        self.duty = duty
        self.log.append({"equipment": equipment, "duty": duty})

    def total_duty(self):
        """Return cumulative duty from all events."""
        return sum(event["duty"] for event in self.log)

    def __repr__(self) -> str:
        return (
            f"EnergyStream(name={self.name}, duty={self.duty}, "
            f"total_logged={self.total_duty()})"
        )
