from .base import Variable

class Velocity(Variable):
    """
    Represents a Velocity quantity.
    Default SI unit: meters per second (m/s).
    
    Example:
    v1 = Velocity(10)           # 10 m/s
    v2 = Velocity(36, "km/hr")  # 36 kilometers per hour
    """

    _conversion = {
        "m/s": 1,
        "km/h": 1 / 3.6,
        "cm/s": 0.01,
        "ft/s": 0.3048,
        "mph": 0.44704  # miles per hour to m/s
    }

    def __init__(self, value, units="m/s"):
        if units not in self._conversion:
            raise ValueError(f"{units} is not a valid unit for Velocity")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "m/s")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise ValueError(f"{target_unit} is not a valid unit for Velocity")
        converted_value = self.value / self._conversion[target_unit]
        return Velocity(converted_value, target_unit)

    def __add__(self, other):
        if not isinstance(other, Velocity):
            raise TypeError("Addition only allowed between Velocity objects")
        result_in_base = self.value + other.value
        return Velocity(result_in_base / self._conversion[self.original_unit], self.original_unit)

    def __eq__(self, other):
        return isinstance(other, Velocity) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"
