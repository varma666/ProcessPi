from .base import Variable

class Mass(Variable):
    """
    Represents a Mass quantity.
    Default SI unit: Kilogram (kg).

    Example:
    m1 = Mass(500, "g")
    m2 = Mass(2, "kg")
    """

    _conversion = {
        "kg": 1,
        "g": 0.001,
        "mg": 0.000001,
        "ton": 1000,
        "lb": 0.453592,
        "oz": 0.0283495,
        "mt": 1000,         # metric ton
        "ug": 1e-9
    }

    def __init__(self, value, units="kg"):
        if value < 0:
            raise ValueError("Mass must be non-negative")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for Mass")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "kg")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for Mass")
        converted_value = self.value / self._conversion[target_unit]
        return Mass(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, Mass):
            raise TypeError("Addition only supported between Mass instances")
        total = self.value + other.value
        return Mass(round(total, 6), "kg")

    def __eq__(self, other):
        return isinstance(other, Mass) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"