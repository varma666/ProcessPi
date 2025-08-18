# processpi/pipelines/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict


class PipelineBase(ABC):
    """
    Abstract base class for all pipeline-related calculations in ProcessPI.
    
    Notes:
    - Keeps parameter handling and validation generic.
    - Specific pipe attributes (diameter, schedule, roughness, material)
      are defined in `pipes.py` and should be used there.
    """

    def __init__(self, **kwargs):
        """
        Initialize a pipeline calculation with input parameters.

        Args:
            **kwargs: Arbitrary keyword arguments for inputs.
        """
        self.params = kwargs

    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """
        Perform the pipeline calculation.
        
        Must be implemented by subclasses.

        Returns:
            dict: Results of the calculation in key-value format.
        """
        pass

    def get_param(self, key: str, default: Any = None) -> Any:
        """
        Safely fetch an input parameter.

        Args:
            key (str): Parameter name.
            default (Any): Default value if key not found.

        Returns:
            Any: The value of the parameter or the default.
        """
        return self.params.get(key, default)

    def validate_required(self, required_keys: list):
        """
        Ensure that required input parameters are present.

        Args:
            required_keys (list): List of required parameter names.

        Raises:
            ValueError: If any required parameter is missing.
        """
        missing = [k for k in required_keys if k not in self.params]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    def _getattr(self, attr_name: str, default: Any = None) -> Any:
        """
        Safely fetch an attribute from the pipeline instance.

        Args:
            attr_name (str): Name of the attribute.
            default (Any): Default value if attribute not found.

        Returns:
            Any: The value of the attribute or the default.
        """
        return getattr(self, attr_name, default)
