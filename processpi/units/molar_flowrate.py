from .base import Variable

class MolarFlowRate(Variable):
    """
    Represents a Molar Flow Rate quantity.
    Default SI unit: mol/s.

    Example:
    n1 = MolarFlowRate(100, "mol/h")
    n2 = MolarFlowRate(0.5, "kmol/s")
    """

    _conversion = {
        "mol/s": 1,
        "kmol/s": 1e3,
        "mol/min": 1 / 60,
        "mol/h": 1 / 3600,
        "kmol/min": 1e3 / 60,
        "kmol/h": 1e3 / 3600,
        "mmol/s": 1e-3,
        "mmol/min": 1e-3 / 60,
        "mmol/h": 1e-3 / 3600,
    }

    def __init__(self, value, units="mol/s"):
        if value < 0:
            raise ValueError("Molar flow rate must be non-negative")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for MolarFlowRate")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "mol/s")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for MolarFlowRate")
        converted_value = self.value / self._conversion[target_unit]
        return MolarFlowRate(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, MolarFlowRate):
            raise TypeError("Addition only supported between MolarFlowRate instances")
        total = self.value + other.value
        return MolarFlowRate(round(total, 6), "mol/s")

    def __eq__(self, other):
        return isinstance(other, MolarFlowRate) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        return f"{round(self.original_value, 6)} {self.original_unit}"
