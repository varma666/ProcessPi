from .base import Variable

class HeatOfVaporization(Variable):
    """
    Represents Heat of Vaporization.
    Default SI unit: J/kg (Joules per kilogram)

    Example:
    hv1 = HeatOfVaporization(2257000)         # 2.257 MJ/kg
    hv2 = HeatOfVaporization(540, "cal/g")    # 540 cal/g = ~2.259 MJ/kg
    """

    _conversion = {
        "J/kg": 1,
        "kJ/kg": 1e3,
        "MJ/kg": 1e6,
        "cal/g": 4184,      # 1 cal/g = 4184 J/kg
        "BTU/lb": 2326      # 1 BTU/lb ≈ 2326 J/kg
    }

    def __init__(self, value, units="J/kg"):
        if value < 0:
            raise ValueError("Heat of Vaporization must be a non-negative value")
        if units not in self._conversion:
            raise ValueError(f"{units} is not a valid unit for Heat of Vaporization")
        base_value = round(value * self._conversion[units], 10)
        super().__init__(base_value, "J/kg")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise ValueError(f"{target_unit} is not a valid unit for Heat of Vaporization")
        converted_value = self.value / self._conversion[target_unit]
        return HeatOfVaporization(converted_value, target_unit)

    def __add__(self, other):
        if not isinstance(other, HeatOfVaporization):
            raise TypeError("Addition only allowed between HeatOfVaporization objects")
        result_in_base = self.value + other.value
        return HeatOfVaporization(result_in_base / self._conversion[self.original_unit], self.original_unit)

    def __eq__(self, other):
        return isinstance(other, HeatOfVaporization) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"