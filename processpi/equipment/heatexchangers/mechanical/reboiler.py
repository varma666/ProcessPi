"""
Deprecated compatibility module.

Reboiler behavior is now handled by unified ShellAndTube(mode="reboiler").
"""

from typing import Dict, Any

from ..base import HeatExchanger
from .shell_tube import ShellAndTube


class Reboiler(ShellAndTube):
    def __init__(self, name: str = "Reboiler", **kwargs):
        super().__init__(name=name, mode="reboiler", **kwargs)


# Backward-compatible alias from previous refactor cycle.
ReboilerHeatExchanger = Reboiler


def design_reboiler(hx: HeatExchanger, **kwargs) -> Dict[str, Any]:
    """Backward-compatible design entrypoint for reboiler mode."""
    if isinstance(hx, ShellAndTube):
        hx.mode = "reboiler"
        return hx._design_shelltube(**kwargs)
    tmp = Reboiler(name=getattr(hx, "name", "Reboiler"))
    tmp.inlets["hot_in"] = getattr(hx, "hot_in", None)
    tmp.inlets["cold_in"] = getattr(hx, "cold_in", None)
    tmp.outlets["hot_out"] = getattr(hx, "hot_out", None)
    tmp.outlets["cold_out"] = getattr(hx, "cold_out", None)
    tmp._collect_base_data()
    result = tmp._design_shelltube(**kwargs)
    hx.design_results = result
    return result
