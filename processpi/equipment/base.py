# processpi/equipment/base.py
from collections import OrderedDict
from typing import Dict, Iterable, Iterator, List, Literal, Optional

from ..streams import MaterialStream


class PortMap(dict):
    """
    Dict-like port container with backward compatibility for list-style indexing.

    - Preferred usage: map by port name, e.g. ``ports['in']``.
    - Legacy compatibility: integer index access remains supported, e.g. ``ports[0]``.
    - Iteration yields stream values (legacy list-like behavior).
    """

    def __init__(self, names: Optional[Iterable[str]] = None):
        names = list(names or [])
        self._order: List[str] = list(names)
        super().__init__(OrderedDict((name, None) for name in names))

    def _name_from_index(self, idx: int) -> str:
        if idx < 0 or idx >= len(self._order):
            raise IndexError(f"Port index {idx} out of range (max={len(self._order)-1})")
        return self._order[idx]

    def add_port(self, name: str) -> None:
        if name in self:
            return
        self._order.append(name)
        super().__setitem__(name, None)

    def has_port(self, name: str) -> bool:
        return name in self

    def __getitem__(self, key):
        if isinstance(key, int):
            key = self._name_from_index(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self._name_from_index(key)
        elif isinstance(key, str) and key not in self:
            self.add_port(key)
        super().__setitem__(key, value)

    def __iter__(self) -> Iterator:
        # Preserve list-like semantics used by existing equipment code.
        return iter(self.values())

    def values_ordered(self) -> List[Optional[MaterialStream]]:
        return [dict.__getitem__(self, name) for name in self._order]


class Equipment:
    """
    Base class for all equipment units.

    Canonical interface:
    - self.inlets:  dict[str, MaterialStream|None]
    - self.outlets: dict[str, MaterialStream|None]

    Backward compatibility:
    - list-style indexing (e.g., ``self.inlets[0]``) still works via PortMap.
    """

    def __init__(
        self,
        name: str,
        inlet_ports: int = 0,
        outlet_ports: int = 0,
        inlet_names: Optional[List[str]] = None,
        outlet_names: Optional[List[str]] = None,
    ):
        self.name = name

        if inlet_names is None:
            inlet_names = ["in"] if inlet_ports == 1 else [f"in{i+1}" for i in range(inlet_ports)]
        if outlet_names is None:
            outlet_names = ["out"] if outlet_ports == 1 else [f"out{i+1}" for i in range(outlet_ports)]

        self.inlets: PortMap = PortMap(inlet_names)
        self.outlets: PortMap = PortMap(outlet_names)

    def connect_inlet(self, port_name: str, stream: MaterialStream) -> None:
        if not self.inlets.has_port(port_name):
            raise ValueError(f"{self.name}: inlet port '{port_name}' is not defined.")
        if self.inlets[port_name] is not None:
            raise ValueError(f"{self.name}: inlet port '{port_name}' already connected.")
        self.inlets[port_name] = stream

    def connect_outlet(self, port_name: str, stream: MaterialStream) -> None:
        if not self.outlets.has_port(port_name):
            raise ValueError(f"{self.name}: outlet port '{port_name}' is not defined.")
        if self.outlets[port_name] is not None:
            raise ValueError(f"{self.name}: outlet port '{port_name}' already connected.")
        self.outlets[port_name] = stream

    def attach_stream(self, stream: MaterialStream, port: Literal["inlet", "outlet"], index: int = 0):
        """
        Backward-compatible stream attach by indexed port.
        """
        if not isinstance(stream, MaterialStream):
            raise TypeError(f"Expected MaterialStream, got {type(stream).__name__}")

        if port == "inlet":
            name = self.inlets._name_from_index(index)
            self.connect_inlet(name, stream)
        elif port == "outlet":
            name = self.outlets._name_from_index(index)
            self.connect_outlet(name, stream)
        else:
            raise ValueError("port must be 'inlet' or 'outlet'")

    def __repr__(self) -> str:
        return (
            f"<Equipment {self.name}, "
            f"inlets={list(self.inlets.keys())}, outlets={list(self.outlets.keys())}>"
        )
