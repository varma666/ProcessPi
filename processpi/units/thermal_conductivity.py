from .base import Variable

class ThermalConductivity(Variable):
    """
    Represents Thermal Conductivity of a material.
    Default SI unit: W/mK (Watts per meter-Kelvin)

    Example:
    k = ThermalConductivity(0.5, "W/mK")
    """

    _conversion = {
        "W/mK": 1,
        "kW/mK": 1000,
        "cal/scmC": 418.4,       # 1 cal/s·cm·°C ≈ 418.4 W/m·K
        "BTU/hftF": 1.730735,   # 1 BTU/hr·ft·°F ≈ 1.730735 W/m·K
    }

    def __init__(self, value, units="W/mK"):
        if value < 0:
            raise ValueError("Thermal conductivity cannot be negative.")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for ThermalConductivity")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "W/mK")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for ThermalConductivity")
        converted_value = self.value / self._conversion[target_unit]
        return ThermalConductivity(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, ThermalConductivity):
            raise TypeError("Addition only supported between ThermalConductivity instances")
        total = self.value + other.value
        return ThermalConductivity(round(total, 6), "W/mK")

    def __eq__(self, other):
        return isinstance(other, ThermalConductivity) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"