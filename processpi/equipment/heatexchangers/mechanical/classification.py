from typing import Optional, Dict, Any
from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers.base import HeatExchanger
from .doublepipe import design_doublepipe
from .shell_tube import design_shelltube
from .condenser import design_condenser
from .evaporator import design_evaporator
from .reboiler import design_reboiler

class HeatExchanger(HeatExchanger):  # extending your existing class
    def design(self, module: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Fully self-contained design:
        - Automatically assigns hot/cold streams based on temperature
        - Automatically selects module if not provided (Condenser, Evaporator, Reboiler, DoublePipe, ShellTube)
        - Delegates to respective design function
        """

        # --- Auto-assign streams if missing ---
        streams = [s for s in [self.hot_in, self.hot_out, self.cold_in, self.cold_out]
                   if isinstance(s, MaterialStream) and s.temperature is not None]
        if len(streams) < 2:
            raise ValueError("At least two streams with temperature required for auto-selection.")

        sorted_streams = sorted(streams, key=lambda s: s.temperature.to("K").value, reverse=True)
        hot, cold = sorted_streams[0], sorted_streams[-1]

        # --- Auto-select module if not specified ---
        if module is None:
            hot_comp = getattr(hot, "component", None)
            cold_comp = getattr(cold, "component", None)
            duty_guess = hot.mass_flowrate.to("kg/s").value * hot.cp.to("J/kg-K").value * \
                         abs(hot.temperature.to("K").value - cold.temperature.to("K").value)

            if hasattr(hot_comp, "is_vapor") and hot_comp.is_vapor() and \
               hasattr(cold_comp, "is_liquid") and cold_comp.is_liquid():
                if hasattr(cold, "is_reboiler_liquid") and cold.is_reboiler_liquid():
                    module = "Reboiler"
                else:
                    module = "Condenser"
            elif hasattr(cold_comp, "is_evaporator_liquid") and cold_comp.is_evaporator_liquid():
                module = "Evaporator"
            elif duty_guess < 1e5:
                module = "DoublePipe"
            else:
                module = "ShellTube"

        module = module.lower()

        # --- Delegate to appropriate design function ---
        if module == "doublepipe":
            return design_doublepipe(hot, cold, **kwargs)
        elif module == "shelltube":
            return design_shelltube(hot, cold, **kwargs)
        elif module == "condenser":
            return design_condenser(hot, cold, **kwargs)
        elif module == "evaporator":
            return design_evaporator(hot, cold, **kwargs)
        elif module == "reboiler":
            return design_reboiler(hot, cold, **kwargs)
        else:
            raise ValueError(f"Unknown module '{module}'. Valid options: DoublePipe, ShellTube, Condenser, Evaporator, Reboiler")
