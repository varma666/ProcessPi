# processpi/pipelines/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict


class PipelineBase(ABC):
    """
    Abstract base class for all pipeline-related calculations in the ProcessPI
    simulation suite.

    This class provides a common interface and a set of utility methods for
    handling input parameters and validating them. Subclasses must inherit from
    this class and implement the `calculate` method to perform their specific
    calculations.

    Notes:
        - Parameter handling and validation are kept generic to allow for
          diverse types of pipeline calculations (e.g., pressure drop,
          flow rate, pump sizing).
        - Specific pipe attributes like diameter, schedule, roughness, and material
          are not handled here. They should be managed by specialized classes,
          such as those in `pipes.py`, which will then pass the necessary
          parameters to the calculation classes.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes a pipeline calculation instance with input parameters.

        The parameters are stored in a dictionary, providing a flexible way
        to pass various inputs without a fixed signature.

        Args:
            **kwargs: Arbitrary keyword arguments representing the input
                      parameters for the calculation.
        """
        self.params: Dict[str, Any] = kwargs

    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """
        Abstract method to perform the core pipeline calculation.

        Subclasses must override this method with their specific
        calculation logic.

        Returns:
            dict: A dictionary containing the results of the calculation,
                  with string keys and any type of value.
        """
        pass

    def get_param(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieves an input parameter from the stored parameters.

        This method prevents `KeyError` by returning a default value if the
        parameter is not found.

        Args:
            key (str): The name of the parameter to retrieve.
            default (Any, optional): The value to return if the key is not
                                     found. Defaults to None.

        Returns:
            Any: The value of the specified parameter or the default value.
        """
        return self.params.get(key, default)

    def validate_required(self, required_keys: list[str]) -> None:
        """
        Ensures that all specified required parameters are present.

        If any key in the `required_keys` list is missing from the instance's
        parameters, a `ValueError` is raised.

        Args:
            required_keys (list[str]): A list of string names for the
                                       parameters that are mandatory for
                                       the calculation.

        Raises:
            ValueError: If one or more required parameters are missing from
                        the `self.params` dictionary.
        """
        missing = [k for k in required_keys if k not in self.params]
        if missing:
            # Joins the missing keys into a single, comma-separated string for a
            # clear error message.
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    def _getattr(self, attr_name: str, default: Any = None) -> Any:
        """
        Safely retrieves an attribute from the pipeline instance itself.

        This is a protected helper method (`_` prefix) and is useful for
        accessing attributes that might be dynamically set on the object
        itself, as opposed to input parameters stored in `self.params`.

        Args:
            attr_name (str): The name of the attribute to fetch.
            default (Any, optional): The value to return if the attribute
                                     is not found. Defaults to None.

        Returns:
            Any: The value of the attribute or the provided default.
        """
        return getattr(self, attr_name, default)
