from .base import Variable

class Dimensionless(Variable):
    """
    Represents a dimensionless quantity (e.g., Reynolds number, friction factor).
    Default SI unit: none (unitless).

    Example:
    Re = Dimensionless(5000)   # Reynolds number
    f = Dimensionless(0.02)    # Friction factor
    """

    def __init__(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Dimensionless value must be a number")
        super().__init__(float(value), "")
        self.original_value = float(value)

    def to(self, target_unit=None):
        """
        Conversion is not applicable, but provided for interface consistency.
        """
        return Dimensionless(self.value)

    def __add__(self, other):
        if not isinstance(other, Dimensionless):
            raise TypeError("Addition only supported between Dimensionless instances")
        return Dimensionless(round(self.value + other.value, 6))

    def __mul__(self, other):
        if isinstance(other, Dimensionless):
            return Dimensionless(round(self.value * other.value, 6))
        elif isinstance(other, (int, float)):
            return Dimensionless(round(self.value * other, 6))
        else:
            raise TypeError("Multiplication only supported with Dimensionless or numeric types")

    def __eq__(self, other):
        return isinstance(other, Dimensionless) and self.value == other.value

    def __repr__(self):
        return f"{self.original_value} (dimensionless)"
