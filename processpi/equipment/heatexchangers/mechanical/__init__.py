from typing import Dict, Any

# Import mechanical submodules
from . import classification
from . import basic_params
from . import double_pipe
from . import shell_tube
from . import kern_method
from . import bell_method
from . import condenser
from . import reboiler
from . import evaporator

# Mapping for design_type strings to submodules
_design_type_map = {
    "DoublePipe": double_pipe,
    "ShellAndTube": shell_tube,
    "Condenser": condenser,
    "Reboiler": reboiler,
    "Evaporator": evaporator
}

_design_method_map = {
    "Kern": kern_method,
    "KernMethod": kern_method,
    "Bell": bell_method,
    "BellMethod": bell_method
}

def run_mechanical_design(hx, type: str, method: str = "BellMethod", **kwargs) -> Dict[str, Any]:
    """
    Dispatch mechanical design calculations to the appropriate submodule.
    
    Default method: Bell-Delaware method
    Optional: Kern's method
    """

    method = method or "BellMethod"
    type = type or "Classification"
    if method not in _design_method_map:
        raise ValueError(
            f"Unknown method '{method}'. Available options: {list(_design_method_map.keys())}"
        )
    
    if type not in _design_type_map:
        raise ValueError(
            f"Unknown type '{type}'. Available options: {list(_design_type_map.keys())}"
        )

    module = _design_type_map[type]
    
    return module.run(hx, **kwargs)

