# processpi/equipment/heatexchangers/classification.py

"""
Heat Exchanger Classification & Dispatcher
------------------------------------------
Automatically selects the appropriate heat exchanger module or routes
to a specified module for design calculations.

Usage:
------
from processpi.equipment.heatexchangers.classification import HXDispatcher

hx = HXDispatcher(hot_stream, cold_stream)
hx.design(module="DoublePipe")  # directly calls DoublePipe design
hx.design()  # auto-selects the best exchanger type
"""

from .doublepipe import design_doublepipe
from .shell_tube import design_shelltube
from .condenser import design_condenser
from .evaporator import design_evaporator
from .reboiler import design_reboiler
from typing import Optional, Dict, Any

class HXDispatcher:
    def __init__(self, hot_stream, cold_stream, **kwargs):
        self.hot = hot_stream
        self.cold = cold_stream
        self.kwargs = kwargs

    def _auto_select_module(self) -> str:
        """
        Heuristic for automatic module selection based on streams:
        - Low duty, low flow, simple: DoublePipe
        - High duty, large flow, multi-phase: ShellTube
        - Condensing hot: Condenser
        - Boiling cold: Evaporator / Reboiler
        """
        hot_comp = self.hot.component
        cold_comp = self.cold.component
        duty_guess = self.hot.mass_flowrate.to("kg/s").value * \
                     self.hot.cp.to("J/kg-K").value * abs(self.hot.temperature.to("K").value - self.cold.temperature.to("K").value)

        if hasattr(hot_comp, "is_vapor") and hot_comp.is_vapor() and hasattr(cold_comp, "is_liquid") and cold_comp.is_liquid():
            if hasattr(self.cold, "is_reboiler_liquid") and self.cold.is_reboiler_liquid():
                return "Reboiler"
            return "Condenser"
        elif duty_guess < 1e5:  # small duty: simple double pipe
            return "DoublePipe"
        else:
            return "ShellTube"

    def design(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Design the heat exchanger using the specified or auto-selected module.
        """
        module = module or self._auto_select_module()
        module = module.lower()

        if module == "doublepipe":
            return design_doublepipe(self.hot, self.cold, **self.kwargs)
        elif module == "shelltube":
            return design_shelltube(self.hot, self.cold, **self.kwargs)
        elif module == "condenser":
            return design_condenser(self.hot, self.cold, **self.kwargs)
        elif module == "evaporator":
            return design_evaporator(self.hot, self.cold, **self.kwargs)
        elif module == "reboiler":
            return design_reboiler(self.hot, self.cold, **self.kwargs)
        else:
            raise ValueError(f"Unknown module '{module}'. Valid options: DoublePipe, ShellTube, Condenser, Evaporator, Reboiler")
