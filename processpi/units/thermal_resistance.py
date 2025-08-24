from .base import Variable

class ThermalResistance(Variable):
    """
    Represents Thermal Resistance.
    Default SI unit: K/W (Kelvin per Watt)

    Example:
    r1 = ThermalResistance(0.5, "K/W")
    r2 = ThermalResistance(2, "C/W")
    """

    _conversion = {
        "K/W": 1,
        "C/W": 1,      # °C/W is numerically equivalent to K/W
        "hrft2F/BTU": 0.1761,  # 1 hr·ft²·°F/BTU ≈ 0.1761 K/W
        "m2K/W": 1,   # often used in building materials
    }

    def __init__(self, value, units="K/W"):
        if value <= 0:
            raise ValueError("Thermal resistance must be positive.")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid unit for ThermalResistance")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "K/W")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for ThermalResistance")
        converted_value = self.value / self._conversion[target_unit]
        return ThermalResistance(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, ThermalResistance):
            raise TypeError("Addition only supported between ThermalResistance instances")
        total = self.value + other.value
        return ThermalResistance(round(total, 6), "K/W")

    def __eq__(self, other):
        return isinstance(other, ThermalResistance) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit}"