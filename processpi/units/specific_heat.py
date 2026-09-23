from .base import Variable

class SpecificHeat(Variable):
    """
    Represents Specific Heat Capacity.
    Default SI unit: J/kgK

    Example:
    cp1 = SpecificHeat(4.186, "kJ/kgK")
    cp2 = SpecificHeat(1.0, "cal/gK")
    """

    _conversion = {
        "J/kgK": 1,
        "kJ/kgK": 1000,
        "cal/gK": 4186.8,    # 1 cal/g.K = 4186.8 J/kg.K
        "BTU/lbF": 4186.8,   # 1 BTU/lb.F = 4186.8 J/kg.K
        "kcal/kgK": 4186.8,  # 1 kcal/kg.K = 4186.8 J/kg.K
    }

    def __init__(self, value, units="kJ/kgK"):
        if value < 0:
            raise ValueError("Specific heat must be positive.")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for SpecificHeat")
        base_value = value * self._conversion[units]
        super().__init__(base_value, "J/kgK")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for SpecificHeat")
        converted_value = self.value / self._conversion[target_unit]
        return SpecificHeat(converted_value, target_unit)

    def __add__(self, other):
        if not isinstance(other, SpecificHeat):
            raise TypeError("Addition only supported between SpecificHeat instances")
        total = self.value + other.value
        return SpecificHeat(total, "J/kgK")

    def __eq__(self, other):
        return isinstance(other, SpecificHeat) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"