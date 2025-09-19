from ..units import *

class EnergyStream:
    """
    Represents an energy stream (heat or work transfer).
    Can bind to equipment and log Q/W duties automatically.
    """

    def __init__(self, name: str):
        self.name = name
        self.log = []  # list of dicts {equipment, tag, duty}

    def bind_equipment(self, equipment):
        """Optionally keep reference to equipment if needed later."""
        self.log.append({"equipment": equipment.name, "tag": "bind", "duty": 0.0})

    def record(self, duty: float, tag: str, equipment: str):
        """Log an energy duty (positive = in, negative = out)."""
        self.log.append({"equipment": equipment, "tag": tag, "duty": duty})

    def total_duty(self, tag: Optional[str] = None) -> float:
        """Return cumulative duty, optionally filtered by tag (Q_in, Q_out, W_in, W_out)."""
        if tag:
            return sum(event["duty"] for event in self.log if event["tag"] == tag)
        return sum(event["duty"] for event in self.log)

    def __repr__(self):
        return f"EnergyStream(name={self.name}, total={self.total_duty()}, entries={len(self.log)})"
