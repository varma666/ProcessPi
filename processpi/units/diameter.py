from .base import Variable

class Diameter(Variable):
    """
    Represents a Diameter quantity.
    Default SI unit: meters (m).
    """

    _conversion = {
        "m": 1,
        "cm": 0.01,
        "mm": 0.001,
        "in": 0.0254,
        "ft": 0.3048
    }

    def __init__(self, value, units="m"):
        if value < 0:
            raise ValueError("Diameter must be non-negative")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for Diameter")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "m")
        self.original_value = value
        self.original_unit = units

    def to_base(self) -> float:
        """Return the base (SI) value in meters."""
        return self.value

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for Diameter")
        converted_value = self.value / self._conversion[target_unit]
        # Return a NEW Diameter object with the converted value and unit
        return Diameter(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, Diameter):
            raise TypeError("Addition only supported between Diameter instances")
        total = self.value + other.value
        return Diameter(round(total, 6), "m")

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.to_base() == other.to_base()
        )

    def __hash__(self):
        # hash on immutable tuple
        return hash((self.__class__.__name__, round(self.to_base(), 9)))

    def __repr__(self):
        # A more detailed representation for debugging
        return f"Diameter({self.original_value!r}, {self.original_unit!r})"

    def __str__(self):
        # Human-friendly format for printing
        # This will use the original_value and original_unit set by `to()`
        return f"{self.original_value} {self.original_unit}"
    

