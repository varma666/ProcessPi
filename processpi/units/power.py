from .base import Variable

class Power(Variable):
    """
    Represents a Power quantity.
    Default SI unit: watt (W).

    Example:
    p1 = Power(1000)           # 1000 W
    p2 = Power(1, "kW")        # 1 kilowatt
    p3 = Power(0.5, "MW")      # 0.5 megawatt
    p4 = Power(1.34, "hp")     # 1.34 horsepower
    """

    _conversion = {
        "W": 1,
        "kW": 1000,           # kilowatt to watt
        "MW": 1_000_000,      # megawatt to watt
        "hp": 745.7,          # mechanical horsepower to watt
        "BTU/h": 0.29307107,  # BTU per hour to watt
    }

    def __init__(self, value, units="W"):
        if value < 0:
            raise ValueError("Power must be a non-negative value")
        if units not in self._conversion:
            raise ValueError(f"{units} is not a valid unit for Power")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "W")  # Always store as base unit (watt)
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise ValueError(f"{target_unit} is not a valid unit for Power")
        converted_value = self.value / self._conversion[target_unit]
        return Power(converted_value, target_unit)

    def __add__(self, other):
        if not isinstance(other, Power):
            raise TypeError("Addition only allowed between Power objects")
        result_in_base = self.value + other.value
        return Power(result_in_base / self._conversion[self.original_unit], self.original_unit)

    def __eq__(self, other):
        return isinstance(other, Power) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"