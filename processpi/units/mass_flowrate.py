from .base import Variable

class MassFlowRate(Variable):
    """
    Represents a Mass Flow Rate quantity.
    Default SI unit: kilograms per second (kg/s).

    Example:
    m1 = MassFlowRate(100, "kg/h")
    m2 = MassFlowRate(0.5, "lb/s")
    """

    _conversion = {
        "kg/s": 1,
        "kg/h": 1 / 3600,
        "g/s": 0.001,
        "g/min": 0.001 / 60,
        "g/h": 0.001 / 3600,
        "lb/s": 0.453592,
        "lb/min": 0.453592 / 60,
        "lb/h": 0.453592 / 3600,
        "kg/day": 1 / 86400,
        "t/day": 0.0115740741
    }

    def __init__(self, value, units="kg/s"):
        if value < 0:
            raise ValueError("Mass flow rate must be non-negative")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for MassFlowRate")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "kg/s")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for MassFlowRate")
        converted_value = self.value / self._conversion[target_unit]
        return MassFlowRate(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, MassFlowRate):
            raise TypeError("Addition only supported between MassFlowRate instances")
        total = self.value + other.value
        return MassFlowRate(round(total, 6), "kg/s")

    def __eq__(self, other):
        return isinstance(other, MassFlowRate) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"