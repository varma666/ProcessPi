from .base import Variable

class Area(Variable):
    """
    Represents an Area quantity.
    Default SI unit: Square Meter (m2).

    Example:
    a1 = Area(100, "cm2")
    a2 = Area(0.5, "m2")
    """

    _conversion = {
        "m2": 1,
        "cm2": 0.0001,
        "mm2": 0.000001,
        "km2": 1_000_000,
        "in2": 0.00064516,
        "ft2": 0.092903,
        "yd2": 0.836127,
        "acre": 4046.86,
        "ha": 10000
    }

    def __init__(self, value, units="m2"):
        if value < 0:
            raise ValueError("Area must be non-negative")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for Area")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "m2")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for Area")
        converted_value = self.value / self._conversion[target_unit]
        return Area(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, Area):
            raise TypeError("Addition only supported between Area instances")
        total = self.value + other.value
        return Area(round(total, 6), "m2")

    def __eq__(self, other):
        return isinstance(other, Area) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"