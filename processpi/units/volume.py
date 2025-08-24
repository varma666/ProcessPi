from .base import Variable

class Volume(Variable):
    """
    Represents a Volume quantity.
    Default SI unit: Cubic Meter (m3).

    Example:
    v1 = Volume(1, "L")
    v2 = Volume(0.001, "m3")
    """

    _conversion = {
        "m3": 1,
        "L": 0.001,
        "mL": 0.000001,
        "cm3": 0.000001,
        "ft3": 0.0283168,
        "in3": 0.0000163871,
        "gal": 0.00378541,   # US gallon
        "bbl": 0.158987      # Oil barrel
    }

    def __init__(self, value, units="m3"):
        if value < 0:
            raise ValueError("Volume must be non-negative")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for Volume")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "m3")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for Volume")
        converted_value = self.value / self._conversion[target_unit]
        return Volume(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, Volume):
            raise TypeError("Addition only supported between Volume instances")
        total = self.value + other.value
        return Volume(round(total, 6), "m3")

    def __eq__(self, other):
        return isinstance(other, Volume) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"