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

    def to_base(self):
        """Convert to base SI unit (Pa)."""
        return self.value * self._conversion[self.units]

    def from_base(self, base_value: float, target_units: str):
        """Convert from Pa to target units."""
        if target_units not in self._conversion:
            raise TypeError(f"{target_units} is not a valid unit for Pressure")
        return base_value / self._conversion[target_units]

    def to(self, target_unit):
        """Return new Pressure in target units."""
        base_value = self.to_base()
        converted_value = self.from_base(base_value, target_unit)
        return Pressure(round(converted_value, 4), target_unit)

    def __add__(self, other):
        if not isinstance(other, Pressure):
            raise TypeError("Addition only supported between Pressure instances")
        total_base = self.to_base() + other.to_base()
        return Pressure(self.from_base(total_base, "Pa"), "Pa")

    def __eq__(self, other):
        return isinstance(other, Pressure) and self.to_base() == other.to_base()

    def __repr__(self):
        return f"{self.value} {self.units}"
