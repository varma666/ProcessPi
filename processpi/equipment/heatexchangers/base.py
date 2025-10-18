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
    # Add a setter for hot_in
    @hot_in.setter
    def hot_in(self, stream: MaterialStream): 
        self.inlets[0] = stream

    @property
    def hot_out(self) -> Optional[MaterialStream]: return self.outlets[0]
    # Add a setter for hot_out (optional, but good practice if you want to set it)
    @hot_out.setter
    def hot_out(self, stream: MaterialStream): 
        self.outlets[0] = stream

    @property
    def cold_in(self) -> Optional[MaterialStream]: return self.inlets[1]
    # Add a setter for cold_in
    @cold_in.setter
    def cold_in(self, stream: MaterialStream): 
        self.inlets[1] = stream

    @property
    def cold_out(self) -> Optional[MaterialStream]: return self.outlets[1]
    # Add a setter for cold_out (optional)
    @cold_out.setter
    def cold_out(self, stream: MaterialStream): 
        self.outlets[1] = stream

    # ... hot_stream and cold_stream properties remain the same ...
    @property
    def hot_stream(self) -> Optional[MaterialStream]: return self.hot_in
    @property
    def cold_stream(self) -> Optional[MaterialStream]: return self.cold_in
    @hot_stream.setter
    def hot_stream(self, stream: MaterialStream):
        self.hot_in = stream # This now works because hot_in has a setter! 
    @cold_stream.setter
    def cold_stream(self, stream: MaterialStream):
        self.cold_in = stream # This now works because cold_in has a setter!

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
        from processpi.equipment.heatexchangers.mechanical.classification import HXClassification
        hx_class = HXClassification()
        return hx_class.design(self, module=module, **kwargs)
    
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
