# processpi/equipment/base.py
from typing import List, Optional, Literal
from ..streams import MaterialStream

class Equipment:
    """
    Base class for all equipment units.
    Manages inlet/outlet MaterialStreams and ensures consistent graph connections.
    """

    def __init__(self, name: str, inlet_ports: int = 0, outlet_ports: int = 0):
        self.name = name
        self.inlets: List[Optional[MaterialStream]] = [None] * inlet_ports
        self.outlets: List[Optional[MaterialStream]] = [None] * outlet_ports

    def attach_stream(self, stream: MaterialStream, port: Literal["inlet", "outlet"], index: int = 0):
        """
        Attach a MaterialStream to an inlet or outlet port.
        Automatically wires up the reverse connection (stream ↔ equipment).

        Parameters
        ----------
        stream : MaterialStream
            The stream to connect
        port : "inlet" or "outlet"
            Whether this is an inlet or outlet connection
        index : int
            Port index (for multi-port equipment like mixers/splitters)
        """
        if port == "inlet":
            self.inlets[index] = stream
            stream.connect_outlet(self)   # stream → equipment consistency
        elif port == "outlet":
            self.outlets[index] = stream
            stream.connect_inlet(self)    # stream ← equipment consistency
        else:
            raise ValueError("port must be 'inlet' or 'outlet'")

    def __repr__(self) -> str:
        return f"<Equipment {self.name}, inlets={len(self.inlets)}, outlets={len(self.outlets)}>"
