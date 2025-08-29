class Variable:
    """
    A generic physical variable with value and units.
    Should be subclassed for specific physical types.
    """

    def __init__(self, value: float, units: str):
        self.value = value
        self.units = units

    def __str__(self):
        return f"{self.value} {self.units}"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.value} {self.units}>"

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.to_base() == other.to_base()
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.to_base() < other.to_base()

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.to_base() <= other.to_base()

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.to_base() > other.to_base()

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.to_base() >= other.to_base()

    def __hash__(self):
        # Use tuple of class name + normalized value (in base units) for immutability
        return hash((self.__class__.__name__, self.to_base()))

    # -------------------------------
    # Arithmetic operations
    # -------------------------------
    def __add__(self, other):
        """Add two variables of the same subclass."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Addition is only supported between {self.__class__.__name__} objects")
        base_sum = self.to_base() + other.to_base()
        return self.from_base(base_sum, self.units)

    def __sub__(self, other):
        """Subtract two variables of the same subclass."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Subtraction is only supported between {self.__class__.__name__} objects")
        base_diff = self.to_base() - other.to_base()
        return self.from_base(base_diff, self.units)

    # -------------------------------
    # Conversion placeholders
    # -------------------------------
    def to(self, target_units: str):
        raise NotImplementedError("Override this method in subclass.")

    def to_base(self):
        raise NotImplementedError("Override this method in subclass.")

    def from_base(self, base_value: float, target_units: str):
        raise NotImplementedError("Override this method in subclass.")
    
    def __format__(self, format_spec):
        """
        Formats the VolumetricFlowRate object based on the given format specifier.
        """
        # Get the value to be formatted.
        value = self.original_value
        
        # Apply the format specifier to the numeric value.
        formatted_value = format(value, format_spec)
        
        # Combine the formatted value and the unit.
        return f"{formatted_value} {self.original_unit}"
