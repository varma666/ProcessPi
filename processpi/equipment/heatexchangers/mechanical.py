from typing import Dict, Any

from .base import HeatExchanger


def run_mechanical_design(hx: HeatExchanger, type: str = "ShellAndTube", **kwargs) -> Dict[str, Any]:
    """Compute mechanical design details for supported heat exchanger types."""

    hx_type = [
        "DoublePipe",
        "ShellAndTube",
        "Plate",
        "AirCooled",
        "FinFan",
        "Spiral",
        "BrazedPlate",
        "Hairpin",
        "Other",
    ]
    if type not in hx_type:
        raise ValueError(f"Invalid heat exchanger type. Choose from {hx_type}")

    if type == "DoublePipe":
        from .mechanical.double_pipe import design_doublepipe

        return design_doublepipe(hx, **kwargs)

    if type == "ShellAndTube":
        from .mechanical.shell_tube import design_shelltube

        return design_shelltube(hx, **kwargs)

    raise NotImplementedError(
        f"Mechanical design is not implemented yet for exchanger type '{type}'."
    )
