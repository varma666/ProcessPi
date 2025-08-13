# base.py
from abc import ABC, abstractmethod

class CalculationBase(ABC):
    """
    Abstract base for all calculation modules in processpi.
    """

    def __init__(self, **kwargs):
        """
        Store all input parameters as attributes.
        """
        self.inputs = kwargs
        self.validate_inputs()

    @abstractmethod
    def validate_inputs(self):
        """
        Validate inputs and raise ValueError if invalid.
        """
        pass

    @abstractmethod
    def calculate(self):
        """
        Perform the calculation and return results as a dict.
        """
        pass

    def get_inputs(self):
        """
        Return a dictionary of original inputs.
        """
        return self.inputs

    def to_dict(self):
        """
        Return a dictionary with both inputs and results.
        """
        result = self.calculate()
        return {
            "inputs": self.inputs,
            "results": result
        }
    @staticmethod
    def _get_value(x, name):
        """Return numeric value if x is numeric or x.value if it's a Variable-like object."""
        if hasattr(x, "value"):
            return x.value
        try:
            # accept numpy/scalar numbers
            return float(x)
        except Exception:
            raise TypeError(f"Could not interpret {name} value: {x!r}")
    