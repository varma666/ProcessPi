from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from processpi.streams.material import MaterialStream

from .base import HeatExchanger
from .bell_delaware import BellDelawareHX
from .condenser import CondenserHX
from .double_pipe import DoublePipeHX
from .evaporator import EvaporatorHX
from .reboiler import ReboilerHX
from .shell_and_tube import ShellAndTubeHX


@dataclass
class HeatExchangerResults:
    data: Dict[str, Any]

    def summary(self):
        print("\n=== Heat Exchanger Summary ===")
        print(f"Type: {self.data['hx_type']}")
        print(f"Q: {self.data['Q']:.2f} W")
        print(f"Area: {self.data['Area']:.3f} m2")
        print(f"U_assumed/U_calculated: {self.data['U_assumed']:.2f}/{self.data['U_calculated']:.2f} W/m2K")
        print(f"Status: {self.data['status']}")
        return self.data

    def detailed_summary(self):
        print("\n=== Heat Exchanger Detailed Summary ===")
        for k, v in self.data.items():
            print(f"- {k}: {v}")
        return self.data


class HeatExchangerEngine:
    _map: Dict[str, Type[HeatExchanger]] = {
        "shell_and_tube": ShellAndTubeHX,
        "double_pipe": DoublePipeHX,
        "condenser": CondenserHX,
        "reboiler": ReboilerHX,
        "evaporator": EvaporatorHX,
        "bell_delaware": BellDelawareHX,
    }

    def __init__(self, **kwargs: Any):
        self.data: Dict[str, Any] = {}
        self._results: Optional[HeatExchangerResults] = None
        if kwargs:
            self.fit(**kwargs)

    def fit(self, hot_in: MaterialStream, cold_in: MaterialStream, hot_out: Optional[MaterialStream] = None, cold_out: Optional[MaterialStream] = None, hx_type: Optional[str] = None, **kwargs: Any):
        if not isinstance(hot_in, MaterialStream) or not isinstance(cold_in, MaterialStream):
            raise TypeError("hot_in and cold_in must be MaterialStream objects")
        self.data = {
            "hot_in": hot_in,
            "cold_in": cold_in,
            "hot_out": hot_out,
            "cold_out": cold_out,
            "hx_type": hx_type,
            "specs": kwargs,
        }
        return self

    def _select_hx_type(self) -> str:
        explicit = self.data.get("hx_type")
        if explicit:
            return explicit
        hot_in = self.data["hot_in"]
        hot_out = self.data.get("hot_out")
        cold_out = self.data.get("cold_out")

        if hot_in.phase == "vapor" and hot_out and hot_out.phase == "liquid":
            return "condenser"
        if cold_out and cold_out.phase == "vapor":
            return "reboiler"

        hot_m = hot_in.mass_flow().to("kg/s").value if hot_in.mass_flow() else 0.0
        cold_m = self.data["cold_in"].mass_flow().to("kg/s").value if self.data["cold_in"].mass_flow() else 0.0
        if max(hot_m, cold_m) <= 1.0:
            return "double_pipe"
        return "shell_and_tube"

    def run(self) -> HeatExchangerResults:
        hx_type = self._select_hx_type()
        cls = self._map[hx_type]
        hx = cls(
            hot_in=self.data["hot_in"],
            cold_in=self.data["cold_in"],
            hot_out=self.data.get("hot_out"),
            cold_out=self.data.get("cold_out"),
            **self.data.get("specs", {}),
        )
        self._results = HeatExchangerResults(hx.design())
        return self._results

    def summary(self):
        if not self._results:
            print("No results available for summary.")
            return None
        return self._results.summary()
