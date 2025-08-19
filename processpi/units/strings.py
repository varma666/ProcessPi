from .base import Variable

class StringUnit(Variable):
    """
    Represents a string-based categorical quantity (e.g., flow type, phase, material category).
    Default unit: none (string).

    Example:
    flow = StringUnit("Laminar", "flow_type")
    phase = StringUnit("Gas", "phase_state")
    """

    def __init__(self, value: str, category: str = "string"):
        if not isinstance(value, str):
            raise TypeError("StringUnit value must be a string")
        super().__init__(value, category)
        self.original_value = value
        self.category = category

    def to(self, target_unit=None):
        """
        Conversion is not applicable for string-based units.
        Provided only for interface consistency.
        """
        return StringUnit(self.value, self.category)

    def __eq__(self, other):
        return isinstance(other, StringUnit) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} ({self.category})"
