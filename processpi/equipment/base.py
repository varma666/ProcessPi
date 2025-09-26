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
        Enforces port registration and ensures stream ↔ equipment consistency.

        Parameters
        ----------
        stream : MaterialStream
            The stream to connect
        port : "inlet" or "outlet"
            Whether this is an inlet or outlet connection
        index : int
            Port index (for multi-port equipment like mixers/splitters)
        """
        if not isinstance(stream, MaterialStream):
            raise TypeError(f"Expected MaterialStream, got {type(stream).__name__}")

        if port == "inlet":
            if index >= len(self.inlets) or index < 0:
                raise IndexError(f"Inlet port {index} out of range (max={len(self.inlets)-1})")
            if self.inlets[index] is not None:
                raise ValueError(f"Inlet port {index} of {self.name} already occupied")
            self.inlets[index] = stream
            stream.connect_outlet(self)  # stream → equipment consistency

        elif port == "outlet":
            if index >= len(self.outlets) or index < 0:
                raise IndexError(f"Outlet port {index} out of range (max={len(self.outlets)-1})")
            if self.outlets[index] is not None:
                raise ValueError(f"Outlet port {index} of {self.name} already occupied")
            self.outlets[index] = stream
            stream.connect_inlet(self)  # stream ← equipment consistency

        else:
            raise ValueError("port must be 'inlet' or 'outlet'")

    def __repr__(self) -> str:
        return (
            f"<Equipment {self.name}, "
            f"inlets={len(self.inlets)}, outlets={len(self.outlets)}>"
        )
