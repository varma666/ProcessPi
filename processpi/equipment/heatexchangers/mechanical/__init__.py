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
_design_map = {
    "Classification": classification,
    "BasicParameters": basic_params,
    "DoublePipe": double_pipe,
    "ShellAndTube": shell_tube,
    "KernMethod": kern_method,
    "BellMethod": bell_method,
    "Condenser": condenser,
    "Reboiler": reboiler,
    "Evaporator": evaporator
}

def run_mechanical_design(hx, method: str = "BellMethod", **kwargs) -> Dict[str, Any]:
    """
    Dispatch mechanical design calculations to the appropriate submodule.
    
    Default method: Bell-Delaware method
    Optional: Kern's method
    """
    method = method or "BellMethod"

    if method not in _design_map:
        raise ValueError(
            f"Unknown method '{method}'. Available options: {list(_design_map.keys())}"
        )

    module = _design_map[method]
    return module.run(hx, **kwargs)

