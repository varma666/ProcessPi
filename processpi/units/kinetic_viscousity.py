from .base import Variable

class KineticViscosity(Variable):
    """
    Represents a Kinetic Viscosity quantity.
    Default SI unit: square meters per second (m²/s).
    
    Example:
    kv1 = KineticViscosity(1e-6)               # 1e-6 m²/s
    kv2 = KineticViscosity(1, "cSt")           # 1 centistoke = 1e-6 m²/s
    """

    _conversion = {
        "m2/s": 1,
        "cm2/s": 1e-4,
        "mm2/s": 1e-6,
        "cSt": 1e-6,     # Centistokes
        "St": 1e-4       # Stokes
    }

    def __init__(self, value, units="m2/s"):
        if value < 0:
            raise ValueError("Kinetic viscosity must be a non-negative value")
        if units not in self._conversion:
            raise ValueError(f"{units} is not a valid unit for Kinetic Viscosity")
        base_value = round(value * self._conversion[units], 10)
        super().__init__(base_value, "m2/s")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise ValueError(f"{target_unit} is not a valid unit for Kinetic Viscosity")
        converted_value = self.value / self._conversion[target_unit]
        return KineticViscosity(converted_value, target_unit)

    def __add__(self, other):
        if not isinstance(other, KineticViscosity):
            raise TypeError("Addition only allowed between KineticViscosity objects")
        result_in_base = self.value + other.value
        return KineticViscosity(result_in_base / self._conversion[self.original_unit], self.original_unit)

    def __eq__(self, other):
        return isinstance(other, KineticViscosity) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"
