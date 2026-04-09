from typing import Dict, Any

from .classification import HXClassification
from .double_pipe import design_doublepipe, HXSolver, HXOptimizer, DesignConstraints, AdaptiveHXOptimizer
from .shell_tube import design_shelltube
from .condenser import design_condenser
from .reboiler import design_reboiler
from .evaporator import design_evaporator


_design_type_map = {
    "DoublePipe": design_doublepipe,
    "ShellAndTube": design_shelltube,
    "Condenser": design_condenser,
    "Reboiler": design_reboiler,
    "Evaporator": design_evaporator,
}


def run_mechanical_design(hx, type: str = "ShellAndTube", method: str = "BellMethod", **kwargs) -> Dict[str, Any]:
    """Dispatch mechanical design calculations to the selected heat exchanger model."""

    # Keep argument for backward compatibility; currently unused by design functions.
    _ = method

    if type == "Classification":
        return HXClassification().design(hx, **kwargs)

    if type not in _design_type_map:
        raise ValueError(
            f"Unknown type '{type}'. Available options: {list(_design_type_map.keys()) + ['Classification']}"
        )

    design_fn = _design_type_map[type]
    return design_fn(hx, **kwargs)
