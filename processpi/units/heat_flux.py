from .base import Variable

class HeatFlux(Variable):
    """
    Represents Heat Flux (heat transfer rate per unit area).
    Default SI unit: W/m2 (Watts per square meter)

    Example:
    q = HeatFlux(300, "W/m²")
    """

    _conversion = {
        "W/m2": 1,
        "kW/m2": 1000,
        "W/cm2": 10000,
        "BTU/hft2": 3.1546,  # 1 BTU/hr·ft² ≈ 3.1546 W/m²
        "cal/scm2": 41840,    # 1 cal/s·cm² ≈ 41840 W/m²
    }

    def __init__(self, value, units="W/m2"):
        if value < 0:
            raise ValueError("Heat flux cannot be negative.")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for HeatFlux")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "W/m2")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for HeatFlux")
        converted_value = self.value / self._conversion[target_unit]
        return HeatFlux(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, HeatFlux):
            raise TypeError("Addition only supported between HeatFlux instances")
        total = self.value + other.value
        return HeatFlux(round(total, 6), "W/m2")

    def __eq__(self, other):
        return isinstance(other, HeatFlux) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"