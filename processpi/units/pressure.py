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
        super().__init__(value, units)
        self.original_value = value
        self.original_unit = units

    def to_base(self):
        """Convert to base SI unit (Pa)."""
        return self.value * self._conversion[self.units]

    def from_base(self, base_value: float, target_units: str):
        """Convert from Pa to target units and return a Pressure object."""
        if target_units not in self._conversion:
            raise TypeError(f"{target_units} is not a valid unit for Pressure")
        converted_value = base_value / self._conversion[target_units]
        return Pressure(round(converted_value, 6), target_units)

    def to(self, target_unit):
        """Return new Pressure in target units."""
        base_value = self.to_base()
        return self.from_base(base_value, target_unit)

    def __repr__(self):
        return f"{self.value} {self.units}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"