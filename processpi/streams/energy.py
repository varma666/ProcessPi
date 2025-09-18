from ..units import Power

class EnergyStream:
    """
    Represents an energy stream (heat or work transfer).
    """

    def __init__(self, name: str, duty: Power):
        self.name = name
        self.duty = duty

    def __repr__(self) -> str:
        return f"EnergyStream(name={self.name}, duty={self.duty})"
