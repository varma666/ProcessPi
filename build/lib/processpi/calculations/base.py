from abc import ABC, abstractmethod

class CalculationBase(ABC):
    """
    Abstract base class for all calculation modules in the processpi library.

    This class defines a standard interface and common utility methods for all
    calculation classes, ensuring they have a consistent structure for input
    validation, calculation execution, and result handling. All specific
    calculation classes (e.g., `PressureDropDarcy`, `ReynoldsNumber`) must
    inherit from this class.
    """

    def __init__(self, **kwargs):
        """
        Initializes the calculation object and stores all input parameters.

        The method automatically calls `validate_inputs()` to ensure that the
        provided arguments are valid before the object is fully constructed.

        Args:
            **kwargs: Arbitrary keyword arguments representing the inputs for the
                      specific calculation.
        """
        self.inputs = kwargs
        self.validate_inputs()

    @abstractmethod
    def validate_inputs(self):
        """
        Abstract method to validate the inputs.

        Subclasses must implement this method to check for the presence and
        validity of required inputs. It should raise a `ValueError` if any
        input is missing or invalid.
        """
        pass

    @abstractmethod
    def calculate(self):
        """
        Abstract method to perform the calculation.

        Subclasses must implement this method to execute the core calculation
        logic. The method should return the results, typically as a dictionary
        or a specific unit object.
        """
        pass

    def get_inputs(self):
        """
        Returns the original inputs provided during initialization.

        Returns:
            dict: A dictionary of the input parameters.
        """
        return self.inputs

    def to_dict(self):
        """
        Performs the calculation and returns a dictionary with both inputs and results.

        This method combines the inputs and the output of the `calculate()` method
        into a single, comprehensive dictionary.

        Returns:
            dict: A dictionary containing two keys: "inputs" and "results".
        """
        result = self.calculate()
        return {
            "inputs": self.inputs,
            "results": result
        }

    @staticmethod
    def _get_value(x, name):
        """
        A static utility method to extract the numeric value from an input.

        This method handles both simple numeric types (like `int`, `float`)
        and custom objects that have a `.value` attribute, such as unit objects.
        It raises a `TypeError` if the value cannot be interpreted as a number.

        Args:
            x: The input value, which can be a number or a unit object.
            name (str): The name of the input, used for a more informative
                        error message.

        Returns:
            float: The numeric value of the input.

        Raises:
            TypeError: If the input value cannot be converted to a float.
        """
        if hasattr(x, "value"):
            return x.value
        try:
            # Accept numpy/scalar numbers.
            return float(x)
        except (TypeError, ValueError):
            raise TypeError(f"Could not interpret {name} value: {x!r}")
