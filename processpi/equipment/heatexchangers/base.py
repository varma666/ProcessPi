from __future__ import annotations
from typing import Optional, Dict, Any

from ..base import Equipment
from processpi.streams import MaterialStream, EnergyStream



class HeatExchanger(Equipment):
    """
    Unified HeatExchanger class.
    Combines thermal simulation and mechanical design.
    """

    def __init__(
        self,
        name: str = "HeatExchanger",
        method: str = "LMTD",
        U: Optional[float] = None,
        area: Optional[float] = None,
        effectiveness: Optional[float] = None,
        energy_stream: Optional[EnergyStream] = None,
        simulated_params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, inlet_ports=2, outlet_ports=2)
        self.method = method.upper()
        self.U = U
        self.area = area
        self.effectiveness = effectiveness

        if energy_stream is None:
            self.energy_stream = EnergyStream(name=f"{name}_Q")
        else:
            self.energy_stream = energy_stream

        self.energy_stream.bind_equipment(self)
        self.simulated_params = simulated_params or {}

    # ------------------------
    # Stream attachment
    # ------------------------
    def attach_stream(self, stream: MaterialStream, port: str, index: Optional[int] = None):
        mapping = {"hot_in": 0, "hot_out": 0, "cold_in": 1, "cold_out": 1}
        #print(port)
        if port in ["hot_in", "cold_in"]:
            super().attach_stream(stream, "inlet", mapping[port])
        elif port in ["hot_out", "cold_out"]:
            super().attach_stream(stream, "outlet", mapping[port])
        else:
            raise ValueError(f"Invalid port: {port}")

    @property
    def hot_in(self) -> Optional[MaterialStream]: return self.inlets[0]
    @property
    def hot_out(self) -> Optional[MaterialStream]: return self.outlets[0]
    @property
    def cold_in(self) -> Optional[MaterialStream]: return self.inlets[1]
    @property
    def cold_out(self) -> Optional[MaterialStream]: return self.outlets[1]

    # ------------------------
    # Thermal simulation
    # ------------------------
    def simulate(self) -> Dict[str, Any]:
        from processpi.equipment.heatexchangers import simulation as sim
        """
        Run heat exchanger simulation.
        Delegates calculations to simulation.py
        """
        return sim.run_simulation(self)

    # ------------------------
    # Mechanical design
    # ------------------------

    def design(self, module: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Advanced design with:
        - Automatic hot/cold stream assignment
        - Multi-phase detection: Condenser, Reboiler, Evaporator
        - Zone-wise LMTD/U iterative convergence
        - Subcooling / superheating zones
        - Internally uses HXDispatcher
        """
        from processpi.equipment.heatexchangers.classification import HXDispatcher
        from processpi.equipment.heatexchangers.condenser import design_condenser
        from processpi.equipment.heatexchangers.evaporator import design_evaporator
        from processpi.equipment.heatexchangers.reboiler import design_reboiler
    
        # ------------------------
        # Auto-assign hot and cold streams if missing
        # ------------------------
        if self.hot_in is None or self.cold_in is None:
            streams = [s for s in self.inlets if isinstance(s, MaterialStream)]
            if len(streams) >= 2:
                streams_sorted = sorted(streams, key=lambda s: s.temperature.to("K").value, reverse=True)
                self.hot_in = streams_sorted[0]
                self.cold_in = streams_sorted[-1]
    
        hot = self.hot_in
        cold = self.cold_in
    
        # ------------------------
        # Multi-phase detection
        # ------------------------
        hot_comp = getattr(hot, "component", None)
        cold_comp = getattr(cold, "component", None)
    
        is_hot_vapor = hasattr(hot_comp, "is_vapor") and hot_comp.is_vapor()
        is_cold_liquid = hasattr(cold_comp, "is_liquid") and cold_comp.is_liquid()
    
        hot_sat = hasattr(hot_comp, "saturation_temperature") and abs(hot.temperature.to("K").value - hot_comp.saturation_temperature().to("K").value) < 2.0
        cold_sat = hasattr(cold_comp, "saturation_temperature") and abs(cold.temperature.to("K").value - cold_comp.saturation_temperature().to("K").value) < 2.0
    
        # ------------------------
        # Determine module automatically
        # ------------------------
        if module is None:
            if is_hot_vapor and is_cold_liquid:
                module = "Condenser" if hot_sat else "ShellTube"
            elif hasattr(cold_comp, "is_reboiler_liquid") and cold_comp.is_reboiler_liquid():
                module = "Reboiler"
            elif hasattr(cold_comp, "is_evaporator_liquid") and cold_comp.is_evaporator_liquid():
                module = "Evaporator"
            else:
                duty_guess = hot.mass_flowrate.to("kg/s").value * hot.cp.to("J/kg-K").value * abs(hot.temperature.to("K").value - cold.temperature.to("K").value)
                module = "DoublePipe" if duty_guess < 1e5 else "ShellTube"
    
        # ------------------------
        # Condenser / Evaporator / Reboiler design with zone-wise iteration
        # ------------------------
        if module.lower() == "condenser":
            return design_condenser(hot, cold, **kwargs)
        elif module.lower() == "evaporator":
            return design_evaporator(hot, cold, **kwargs)
        elif module.lower() == "reboiler":
            return design_reboiler(hot, cold, **kwargs)
        else:
            # For standard mechanical exchangers, use HXDispatcher
            dispatcher = HXDispatcher(hot_stream=hot, cold_stream=cold, **kwargs)
            return dispatcher.design(module=module)

    
    def __str__(self):
        return f"Heat Exchanger: {self.name}\n" +\
               f"  Method: {self.method}\n" +\
               f"  U: {self.U}\n" +\
               f"  Area: {self.area}\n" +\
               f"  Effectiveness: {self.effectiveness}\n" +\
               f"  Hot In: {self.hot_in}\n" +\
               f"  Hot Out: {self.hot_out}\n" +\
               f"  Cold In: {self.cold_in}\n" +\
               f"  Cold Out: {self.cold_out}\n" +\
               f"  Energy Stream: {self.energy_stream}\n"
    def __repr__(self):
        return f"HeatExchanger(name={self.name}, method={self.method}, U={self.U}, area={self.area}, effectiveness={self.effectiveness})"
