from .base import Variable

class SpecificHeat(Variable):
    """
    Represents Specific Heat Capacity.
    Default SI unit: kJ/kgK

    Example:
    cp1 = SpecificHeat(4.186, "kJ/kgK")
    cp2 = SpecificHeat(1.0, "cal/gK")
    """

    _conversion = {
        "kJ/kgK": 1,
        "J/kgK": 0.001,
        "cal/gK": 4.1868 * 0.001,   # 1 cal/g.K = 4.1868 kJ/kg.K
        "BTU/lbF": 4.1868 * 2.326,  # approx conversion to kJ/kg.K
        "kcal/kgK": 4.1868
    }

    def __init__(self, value, units="kJ/kgK"):
        if value < 0:
            raise ValueError("Specific heat must be positive.")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for SpecificHeat")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "kJ/kgK")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for SpecificHeat")
        converted_value = self.value / self._conversion[target_unit]
        return SpecificHeat(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, SpecificHeat):
            raise TypeError("Addition only supported between SpecificHeat instances")
        total = self.value + other.value
        return SpecificHeat(round(total, 6), "kJ/kgK")

    def __eq__(self, other):
        return isinstance(other, SpecificHeat) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"