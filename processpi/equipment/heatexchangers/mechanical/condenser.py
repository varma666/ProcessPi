"""
Deprecated compatibility module.

Condenser behavior is now handled by unified ShellAndTube(mode="condenser").
"""

from typing import Dict, Any

from ..base import HeatExchanger
from .shell_tube import ShellAndTube


class Condenser(ShellAndTube):
    def __init__(self, name: str = "Condenser", **kwargs):
        super().__init__(name=name, mode="condenser", **kwargs)


# Backward-compatible alias from previous refactor cycle.
CondenserHeatExchanger = Condenser


def design_condenser(hx: HeatExchanger, **kwargs) -> Dict[str, Any]:
    """Backward-compatible design entrypoint for condenser mode."""
    if isinstance(hx, ShellAndTube):
        hx.mode = "condenser"
        return hx._design_shelltube(**kwargs)
    # Transitional path for generic HeatExchanger instances
    tmp = Condenser(name=getattr(hx, "name", "Condenser"))
    tmp.inlets["hot_in"] = getattr(hx, "hot_in", None)
    tmp.inlets["cold_in"] = getattr(hx, "cold_in", None)
    tmp.outlets["hot_out"] = getattr(hx, "hot_out", None)
    tmp.outlets["cold_out"] = getattr(hx, "cold_out", None)
    tmp._collect_base_data()
    result = tmp._design_shelltube(**kwargs)
    hx.design_results = result
    return result
