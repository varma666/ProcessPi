from .base import Variable

class Viscosity(Variable):
    """
    Represents a viscosity quantity.
    Supports both dynamic viscosity (Pa·s) and kinematic viscosity (m²/s).
    
    Example:
        v1 = Viscosity(1e-3, units="Pa·s")   # Dynamic viscosity
        v2 = Viscosity(1, units="cSt")       # Kinematic viscosity
    """

    _dynamic_conversion = {
        "Pa·s": 1,
        "mPa·s": 1e-3,
        "cP": 1e-3,       # Centipoise
        "P": 0.1          # Poise
    }

    _kinematic_conversion = {
        "m2/s": 1,
        "cm2/s": 1e-4,
        "mm2/s": 1e-6,
        "cSt": 1e-6,
        "St": 1e-4
    }

    def __init__(self, value, units="Pa·s"):
        if value < 0:
            raise ValueError("Viscosity must be a non-negative value")
        
        if units in self._dynamic_conversion:
            self.viscosity_type = "dynamic"
            base_value = round(value * self._dynamic_conversion[units], 10)
            base_unit = "Pa·s"
        elif units in self._kinematic_conversion:
            self.viscosity_type = "kinematic"
            base_value = round(value * self._kinematic_conversion[units], 10)
            base_unit = "m2/s"
        else:
            raise ValueError(f"{units} is not a valid unit for Viscosity")

        super().__init__(base_value, base_unit)
        self.original_value = value
        self.original_unit = units

    def to(self, target_unit):
        if self.viscosity_type == "dynamic":
            if target_unit not in self._dynamic_conversion:
                raise ValueError(f"{target_unit} is not a valid unit for dynamic viscosity")
            converted_value = self.value / self._dynamic_conversion[target_unit]
        elif self.viscosity_type == "kinematic":
            if target_unit not in self._kinematic_conversion:
                raise ValueError(f"{target_unit} is not a valid unit for kinematic viscosity")
            converted_value = self.value / self._kinematic_conversion[target_unit]
        else:
            raise ValueError("Unknown viscosity type")
        
        return Viscosity(converted_value, target_unit)

    def __add__(self, other):
        if not isinstance(other, Viscosity):
            raise TypeError("Addition only allowed between Viscosity objects")
        if self.viscosity_type != other.viscosity_type:
            raise ValueError("Cannot add viscosities of different types")
        result_in_base = self.value + other.value
        conversion_dict = self._dynamic_conversion if self.viscosity_type == "dynamic" else self._kinematic_conversion
        return Viscosity(result_in_base / conversion_dict[self.original_unit], self.original_unit)

    def __eq__(self, other):
        return (
            isinstance(other, Viscosity) and 
            self.value == other.value and 
            self.viscosity_type == other.viscosity_type
        )

    def __repr__(self):
        return f"{self.original_value} {self.original_unit} ({self.viscosity_type})"

    def __str__(self):
        # Ensure print() uses the same human-friendly format
        return f"{round(self.original_value, 6)} {self.original_unit} ({self.viscosity_type})"