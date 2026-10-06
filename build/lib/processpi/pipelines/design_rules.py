"""
Design rules module for ProcessPi pipelines.

This module defines reusable validation rules for pipeline steps, ensuring that each step
is well-formed, inputs/outputs are consistent, and parameters meet expected requirements.
"""

from typing import Any, Dict, List, Callable, Tuple

class DesignRuleError(Exception):
    """Custom exception for design rule violations."""
    pass

class DesignRules:
    """
    Provides static design rule checks for pipeline steps and configurations.
    """

    @staticmethod
    def validate_step_name(name: str) -> None:
        """
        Ensures that the step name is valid (non-empty and alphanumeric with underscores).
        """
        if not name or not name.replace("_", "").isalnum():
            raise DesignRuleError(f"Invalid step name '{name}'. Must be alphanumeric with underscores.")

    @staticmethod
    def validate_inputs_outputs(inputs: List[str], outputs: List[str]) -> None:
        """
        Ensures that inputs and outputs are lists of non-empty strings and do not overlap.
        """
        if not all(isinstance(i, str) and i.strip() for i in inputs):
            raise DesignRuleError("All input names must be non-empty strings.")
        if not all(isinstance(o, str) and o.strip() for o in outputs):
            raise DesignRuleError("All output names must be non-empty strings.")
        if set(inputs) & set(outputs):
            raise DesignRuleError("Inputs and outputs cannot overlap.")

    @staticmethod
    def validate_parameters(params: Dict[str, Any], required: List[str] = None) -> None:
        """
        Ensures that required parameters are present.
        """
        required = required or []
        missing = [p for p in required if p not in params]
        if missing:
            raise DesignRuleError(f"Missing required parameters: {', '.join(missing)}")

    @staticmethod
    def validate_callable(func: Callable, name: str = "") -> None:
        """
        Ensures that a provided function or callable is valid.
        """
        if not callable(func):
            raise DesignRuleError(f"Step '{name}' has invalid function. Must be callable.")

    @staticmethod
    def validate_pipeline_consistency(steps: List[Dict[str, Any]]) -> None:
        """
        Checks that pipeline steps are connected properly, with consistent data flow.
        """
        produced = set()
        for step in steps:
            name = step.get("name", "<unnamed>")
            inputs = step.get("inputs", [])
            outputs = step.get("outputs", [])

            # Ensure all inputs were produced by previous steps
            for i in inputs:
                if i not in produced:
                    raise DesignRuleError(f"Step '{name}' references input '{i}' not produced by previous steps.")

            # Track produced outputs
            for o in outputs:
                if o in produced:
                    raise DesignRuleError(f"Output '{o}' produced multiple times in the pipeline.")
                produced.add(o)

    @staticmethod
    def summary() -> Dict[str, str]:
        """
        Returns a summary of available design rules.
        """
        return {
            "validate_step_name": "Step name must be alphanumeric and may include underscores.",
            "validate_inputs_outputs": "Inputs and outputs must be unique non-empty strings and not overlap.",
            "validate_parameters": "Required parameters must be present in step configuration.",
            "validate_callable": "Each step must define a callable function.",
            "validate_pipeline_consistency": "Pipeline steps must have consistent data flow and no duplicate outputs.",
        }

__all__ = ["DesignRules", "DesignRuleError"]
