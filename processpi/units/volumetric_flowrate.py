from .base import Variable

class VolumetricFlowRate(Variable):
    """
    Represents a Volumetric Flow Rate quantity.
    Default SI unit: Cubic meters per second (m³/s).

    Example:
    v1 = VolumetricFlowRate(2, "m3/h")
    v2 = VolumetricFlowRate(500, "L/min")
    """

    _conversion = {
        "m3/s": 1,
        "m3/h": 1 / 3600,
        "L/s": 1 / 1000,
        "L/min": 1 / (1000 * 60),
        "L/h": 1 / (1000 * 3600),
        "ft3/s": 0.0283168,
        "ft3/min": 0.0283168 / 60,
        "ft3/h": 0.0283168 / 3600,
        "gal/min": 0.00378541 / 60,
        "gal/h": 0.00378541 / 3600
    }

    def __init__(self, value, units="m3/s"):
        if value < 0:
            raise ValueError("Volumetric flow rate must be non-negative")
        if units not in self._conversion:
            raise TypeError(f"{units} is not a valid volumetric flow rate unit")
        base_value = round(value * self._conversion[units], 6)
        super().__init__(base_value, "m3/s")
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if target_unit not in self._conversion:
            raise TypeError(f"{target_unit} is not a valid unit for VolumetricFlowRate")
        converted_value = self.value / self._conversion[target_unit]
        return VolumetricFlowRate(round(converted_value, 6), target_unit)

    def __add__(self, other):
        if not isinstance(other, VolumetricFlowRate):
            raise TypeError("Addition only supported between VolumetricFlowRate instances")
        total = self.value + other.value
        return VolumetricFlowRate(round(total, 6), "m3/s")

    def __eq__(self, other):
        return isinstance(other, VolumetricFlowRate) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} {self.original_unit}"
