from .base import Variable

class Velocity(Variable):
    """
    Represents a Velocity quantity.
    Default SI unit: meters per second (m/s).
    """

    _conversion = {
        "m/s": 1,
        "km/h": 1 / 3.6,
        "cm/s": 0.01,
        "ft/s": 0.3048,
        "mph": 0.44704
    }

    def __init__(self, value, units="m/s"):
        if units not in self._conversion:
            raise ValueError(f"{units} is not a valid unit for Velocity")

        base_value = round(value * self._conversion[units], 9)
        super().__init__(base_value, "m/s")

        self.original_value = round(value, 9)
        self.original_unit = units

    # ---------------------------
    # Conversion Logic
    # ---------------------------
    def to_base(self):
        return self.value

    def from_base(self, base_value, target_units):
        if target_units not in self._conversion:
            raise ValueError(f"{target_units} is not a valid unit for Velocity")
        converted_value = base_value / self._conversion[target_units]
        return Velocity(converted_value, target_units)

    def to(self, target_unit):
        return self.from_base(self.to_base(), target_unit)

    # ---------------------------
    # Display
    # ---------------------------
    def __repr__(self):
        return f"{round(self.original_value, 6)} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"
