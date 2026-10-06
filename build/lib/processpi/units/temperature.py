from .base import Variable

class Temperature(Variable):
    """
    Represents a Temperature quantity.
    Default SI unit: Kelvin (K).

    Example:
    t1 = Temperature(100, "C")      # 100°C
    t2 = Temperature(373.15)        # 373.15 K
    """

    _conversion = {
        "K": lambda x: x,
        "C": lambda x: x + 273.15,
        "F": lambda x: (x - 32) * 5 / 9 + 273.15
    }

    _reverse_conversion = {
        "K": lambda x: x,
        "C": lambda x: x - 273.15,
        "F": lambda x: (x - 273.15) * 9 / 5 + 32
    }

    def __init__(self, value, units="K"):
        if units not in self._conversion:
            raise ValueError(f"{units} is not a valid unit for Temperature")
        base_value = round(self._conversion[units](value), 4)
        super().__init__(base_value, "K")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._reverse_conversion:
            raise ValueError(f"{target_unit} is not a valid target unit for Temperature")
        converted_value = self._reverse_conversion[target_unit](self.value)
        return Temperature(round(converted_value, 4), target_unit)

    def __add__(self, other):
        raise TypeError("Direct addition of two temperatures is not physically meaningful")

    def __sub__(self, other):
        if not isinstance(other, Temperature):
            raise TypeError("Subtraction only allowed between Temperature objects")
        return self.value - other.value  # Difference in Kelvin

    def __eq__(self, other):
        return isinstance(other, Temperature) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"