from .base import Variable

class Length(Variable):
    """
    Represents a Length quantity Variable.
    Default SI unit: Meters (m).
    
    Example:
    length = Length(30)           # 30 meters
    length = Length(30, "in")     # 30 inches
    """

    _conversion = {
        "m": 1,
        "cm": 0.01,
        "mm": 0.001,
        "in": 0.0254,
        "ft": 0.3048,
        "km": 1000
    }

    def __init__(self, value, units="m"):
        if value < 0:
            raise ValueError("Length must be positive")
        elif units not in self._conversion:
            raise ValueError(f"{units} is not a valid unit for Length")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "m")  # Always store as base unit (meters)
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise ValueError(f"{target_unit} is not a valid unit for Length")
        converted_value = self.value / self._conversion[target_unit]
        return Length(converted_value, target_unit)

    def __add__(self, other):
        if not isinstance(other, Length):
            raise TypeError("Addition only allowed between Length objects")
        result_in_base = self.value + other.value
        return Length(result_in_base / self._conversion[self.original_unit], self.original_unit)

    def __eq__(self, other):
        return isinstance(other, Length) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"