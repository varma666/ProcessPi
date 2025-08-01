from .base import Variable

class Pressure(Variable):
    """
    Represents a Pressure quantity.
    Default SI unit: Pascal (Pa).

    Example:
    p1 = Pressure(1, "atm")
    p2 = Pressure(101325, "Pa")
    """

    _conversion = {
        "Pa": 1,
        "kPa": 1_000,
        "MPa": 1_000_000,
        "bar": 100_000,
        "atm": 101_325,
        "psi": 6_894.76,
        "mmHg": 133.322,
        "torr": 133.322
    }

    def __init__(self, value, units="Pa"):
        if value < 0:
            raise ValueError("Pressure must be non-negative")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for Pressure")
        base_value = round(value * self._conversion[units], 4)
        super().__init__(base_value, "Pa")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for Pressure")
        converted_value = self.value / self._conversion[target_unit]
        return Pressure(round(converted_value, 4), target_unit)

    def __add__(self, other):
        if not isinstance(other, Pressure):
            raise TypeError("Addition only supported between Pressure instances")
        total = self.value + other.value
        return Pressure(round(total, 4), "Pa")

    def __eq__(self, other):
        return isinstance(other, Pressure) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"
