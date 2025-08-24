from .base import Variable

class HeatTransferCoefficient(Variable):
    """
    Represents Heat Transfer Coefficient.
    Default SI unit: W/m2K (Watts per square meter-Kelvin)

    Example:
    h = HeatTransferCoefficient(200, "W/m2K")
    """

    _conversion = {
        "W/m2K": 1,
        "kW/m2K": 1000,
        "cal/scm2C": 41840,          # 1 cal/s·cm²·°C ≈ 41840 W/m²·K
        "BTU/hft2F": 5.678263,      # 1 BTU/hr·ft²·°F ≈ 5.678263 W/m²·K
    }

    def __init__(self, value, units="W/m2K"):
        if value < 0:
            raise ValueError("Heat transfer coefficient cannot be negative.")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for HeatTransferCoefficient")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "W/m2K")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for HeatTransferCoefficient")
        converted_value = self.value / self._conversion[target_unit]
        return HeatTransferCoefficient(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, HeatTransferCoefficient):
            raise TypeError("Addition only supported between HeatTransferCoefficient instances")
        total = self.value + other.value
        return HeatTransferCoefficient(round(total, 6), "W/m2K")

    def __eq__(self, other):
        return isinstance(other, HeatTransferCoefficient) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"