from .base import Variable

class HeatFlow(Variable):
    """
    Represents Heat Flow (total heat transfer rate).
    Default SI unit: W (Watts)

    Example:
        Q = HeatFlow(5000, "W")
        Q.to("kW")  # -> 5.0 kW
    """

    _conversion = {
        "W": 1,
        "kW": 1000,
        "MW": 1e6,
        "BTU/h": 0.29307107,   # 1 BTU/h ≈ 0.29307107 W
        "cal/s": 4.184,        # 1 cal/s = 4.184 W
        "kcal/h": 1.163,       # 1 kcal/h ≈ 1.163 W
    }

    def __init__(self, value, units="W"):
        if value < 0:
            raise ValueError("Heat flow cannot be negative.")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for HeatFlow")

        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "W")

        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for HeatFlow")
        converted_value = self.value / self._conversion[target_unit]
        return HeatFlow(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, HeatFlow):
            raise TypeError("Addition only supported between HeatFlow instances")
        total = self.value + other.value
        return HeatFlow(round(total, 6), "W")

    def __eq__(self, other):
        return isinstance(other, HeatFlow) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        return f"{round(self.original_value, 6)} {self.original_unit}"
