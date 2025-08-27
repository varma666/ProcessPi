# processpi/pipelines/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PipelineBase(ABC):
    """
    Abstract base class for all pipeline-related components and calculations
    in the ProcessPI simulation suite.

    Provides:
        - A unified way to store metadata like `name`
        - A flexible params dictionary for input configuration
        - Utility methods for safe parameter access and validation
    """

    def __init__(self, name: Optional[str] = None, **kwargs: Any) -> None:
        """
        Initialize a pipeline component or calculation with metadata and parameters.

        Args:
            name (str, optional): Descriptive name of this pipeline object.
            **kwargs (Any): Arbitrary parameters for configuration.
        """
        self.name: str = name or self.__class__.__name__
        self.params: Dict[str, Any] = kwargs

    # -------------------------------------------------------------------------
    # Abstract method that must be implemented by all subclasses
    # -------------------------------------------------------------------------
    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """
        Perform the core calculation for the pipeline object.

        Must be implemented by subclasses.

        Returns:
            dict: A dictionary containing calculation results.
        """
        pass

    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------
    def get_param(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a parameter safely with a default fallback.

        Args:
            key (str): Parameter name.
            default (Any, optional): Value to return if key not found.

        Returns:
            Any: The parameter value or default.
        """
        return self.params.get(key, default)

    def validate_required(self, required_keys: list[str]) -> None:
        """
        Validate that required parameters are present in `self.params`.

        Args:
            required_keys (list[str]): Required parameter names.

        Raises:
            ValueError: If any required parameters are missing.
        """
        missing = [k for k in required_keys if k not in self.params]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    def _getattr(self, attr_name: str, default: Any = None) -> Any:
        """
        Safely retrieve an attribute from the instance itself.

        Args:
            attr_name (str): Attribute name.
            default (Any, optional): Value to return if not found.

        Returns:
            Any: Attribute value or default.
        """
        return getattr(self, attr_name, default)

    def __repr__(self) -> str:
        """
        Developer-friendly representation of the object.
        """
        return f"<{self.__class__.__name__} name='{self.name}' params={self.params}>"
