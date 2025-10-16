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
        Unified design interface.
        Delegates to HXClassification which handles multi-phase, 
        subcooling/superheating, zone-wise U/LMTD iterations, etc.
        """
        from processpi.equipment.heatexchangers.classification import HXClassification
        hx_class = HXClassification(hot=self.hot_in, cold=self.cold_in)
        return hx_class.design(module=module, **kwargs)
    
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
