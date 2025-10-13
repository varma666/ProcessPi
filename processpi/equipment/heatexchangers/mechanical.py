from typing import Dict, Any
from .base import HeatExchanger

def run_mechanical_design(hx: HeatExchanger, type: str = "ShellAndTube", **kwargs) -> Dict[str, Any]:
    """
    Compute tube/shell sizing, thickness, pressure drop, layout, etc.
    """

    hx_type = ["DoublePipe", "ShellAndTube", "Plate", "AirCooled", "FinFan", "Spiral", "BrazedPlate", "Hairpin", "Other"]
    if type not in hx_type:
        raise ValueError(f"Invalid heat exchanger type. Choose from {hx_type}")


    results: Dict[str, Any] = {}

    if type == "DoublePipe":
        from .mechanical.double_pipe import run
        results = design_double_pipe(hx, **kwargs)
    return results

