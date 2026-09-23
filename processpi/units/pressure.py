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
        # Stored in Pa, like every other unit class stores its SI base, so that
        # `.value` means the same thing whatever unit the pressure was given in.
        super().__init__(value * self._conversion[units], "Pa")
        self.original_value = value
        self.original_unit = units

    def to_base(self):
        """Return the value in the base SI unit (Pa)."""
        return self.value

    def from_base(self, base_value: float, target_units: str):
        """Convert from Pa to target units and return a Pressure object."""
        if target_units not in self._conversion:
            raise TypeError(f"{target_units} is not a valid unit for Pressure")
        converted_value = base_value / self._conversion[target_units]
        return Pressure(converted_value, target_units)

    def to(self, target_unit):
        """Return new Pressure in target units."""
        return self.from_base(self.value, target_unit)

    def __add__(self, other):
        if not isinstance(other, Pressure):
            raise TypeError("Addition is only supported between Pressure objects")
        return self.from_base(self.value + other.value, self.original_unit)

    def __sub__(self, other):
        if not isinstance(other, Pressure):
            raise TypeError("Subtraction is only supported between Pressure objects")
        return self.from_base(self.value - other.value, self.original_unit)

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"
