"""
Deprecated compatibility module.

Evaporator behavior is now handled by unified ShellAndTube(mode="evaporator").
"""

from typing import Dict, Any

from ..base import HeatExchanger
from .shell_tube import ShellAndTube


class Evaporator(ShellAndTube):
    def __init__(self, name: str = "Evaporator", **kwargs):
        super().__init__(name=name, mode="evaporator", **kwargs)


# Backward-compatible alias from previous refactor cycle.
EvaporatorHeatExchanger = Evaporator


def design_evaporator(hx: HeatExchanger, **kwargs) -> Dict[str, Any]:
    """Backward-compatible design entrypoint for evaporator mode."""
    if isinstance(hx, ShellAndTube):
        hx.mode = "evaporator"
        return hx._design_shelltube(**kwargs)
    tmp = Evaporator(name=getattr(hx, "name", "Evaporator"))
    tmp.inlets["hot_in"] = getattr(hx, "hot_in", None)
    tmp.inlets["cold_in"] = getattr(hx, "cold_in", None)
    tmp.outlets["hot_out"] = getattr(hx, "hot_out", None)
    tmp.outlets["cold_out"] = getattr(hx, "cold_out", None)
    tmp._collect_base_data()
    result = tmp._design_shelltube(**kwargs)
    hx.design_results = result
    return result
