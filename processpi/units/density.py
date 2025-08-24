from .base import Variable

class Density(Variable):
    """
    Represents a Density quantity.
    Default SI unit: kilograms per cubic meter (kg/m³).
    
    Example:
    d1 = Density(1000)             # 1000 kg/m³
    d2 = Density(1, "g/cm³")       # 1 gram per cubic centimeter
    """

    _conversion = {
        "kg/m3": 1,
        "g/cm3": 1000,
        "g/mL": 1000,
        "lb/ft3": 16.0185,
        "lb/in3": 27679.9
    }

    def __init__(self, value, units="kg/m3"):
        if value < 0:
            raise ValueError("Density must be a non-negative value")
        if units not in self._conversion:
            raise ValueError(f"{units} is not a valid unit for Density")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "kg/m3")  # Always store as base unit (kg/m³)
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise ValueError(f"{target_unit} is not a valid unit for Density")
        converted_value = self.value / self._conversion[target_unit]
        return Density(converted_value, target_unit)

    def __add__(self, other):
        if not isinstance(other, Density):
            raise TypeError("Addition only allowed between Density objects")
        result_in_base = self.value + other.value
        return Density(result_in_base / self._conversion[self.original_unit], self.original_unit)

    def __eq__(self, other):
        return isinstance(other, Density) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"
    
    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"
