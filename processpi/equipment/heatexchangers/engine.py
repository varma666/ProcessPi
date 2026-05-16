from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from processpi.streams.material import MaterialStream

from .base import HeatExchanger
from .condenser import CondenserHX
from .double_pipe import DoublePipeHX
from .evaporator import EvaporatorHX
from .reboiler import ReboilerHX
from .shell_and_tube import ShellAndTubeHX


@dataclass
class HeatExchangerResults:
    data: Dict[str, Any]

    def summary(self) -> str:
        return (
            f"Heat Exchanger Summary\n"
            f"Type: {self.data.get('hx_type')}\n"
            f"Q: {self.data.get('Q', 0.0):.2f} kW\n"
            f"Area: {self.data.get('Area', 0.0):.3f} m2\n"
            f"U_assumed/U_calculated: {self.data.get('U_assumed', 0.0):.2f}/{self.data.get('U_calculated', 0.0):.2f} W/m2K\n"
            f"Status: {self.data.get('status', 'UNKNOWN')}"
        )

    def detailed_summary(self) -> Dict[str, Any]:
        return self.data


class HeatExchangerEngine:
    _map: Dict[str, Type[HeatExchanger]] = {
        "shell_and_tube": ShellAndTubeHX,
        "double_pipe": DoublePipeHX,
        "condenser": CondenserHX,
        "reboiler": ReboilerHX,
        "evaporator": EvaporatorHX,
        "bell_delaware": ShellAndTubeHX,
    }

    def __init__(self, name: Optional[str] = None, method: str = "kern", **kwargs: Any):
        self.name = name
        self.method = method.lower()
        if self.method not in {"kern", "bell_delaware"}:
            raise ValueError("method must be 'kern' or 'bell_delaware'")
        self.data: Dict[str, Any] = {}
        self._results: Optional[HeatExchangerResults] = None
        if kwargs:
            self.fit(**kwargs)

    def fit(
        self,
        hot_in: MaterialStream,
        cold_in: MaterialStream,
        hot_out: Optional[MaterialStream] = None,
        cold_out: Optional[MaterialStream] = None,
        hx_type: Optional[str] = None,
        **kwargs: Any,
    ):
    
        if (
            not isinstance(hot_in, MaterialStream)
            or not isinstance(cold_in, MaterialStream)
        ):
            raise TypeError(
                "hot_in and cold_in must "
                "be MaterialStream objects"
            )
    
        # ======================================================
        # UPDATE METHOD IF PROVIDED
        # ======================================================
    
        method = kwargs.get("method")
    
        if method is not None:
    
            self.method = method.lower()
    
            if self.method not in {
                "kern",
                "bell_delaware",
            }:
    
                raise ValueError(
                    "method must be "
                    "'kern' or 'bell_delaware'"
                )
    
        # ======================================================
        # STORE DATA
        # ======================================================
    
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
    
        # ======================================================
        # HX TYPE SELECTION
        # ======================================================
    
        hx_type = self._select_hx_type()
    
        if (
            hx_type == "shell_and_tube"
            and self.method == "bell_delaware"
        ):
            hx_type = "bell_delaware"
    
        cls = self._map[hx_type]
    
        # ======================================================
        # CREATE HX OBJECT
        # ======================================================
        specs = dict(self.data.get("specs", {}))
        
        # Prevent duplicate keyword issue
        specs.pop("method", None)
        
        hx = cls(
            hot_in=self.data["hot_in"],
            cold_in=self.data["cold_in"],
            hot_out=self.data.get("hot_out"),
            cold_out=self.data.get("cold_out"),
            method=(
                self.method
                if issubclass(cls, ShellAndTubeHX)
                else "kern"
            ),
            **specs,
        )
    
        # ======================================================
        # MODE SELECTION
        # ======================================================
    
        mode = (
            self.data
            .get("specs", {})
            .get("mode", "design")
            .lower()
        )
    
    
        # ======================================================
        # DESIGN MODE
        # ======================================================
    
        if mode == "design":
    
            results = hx.design()
    
        # ======================================================
        # RATE MODE
        # ======================================================
    
        elif mode == "rate":
    
            required_geometry = [
                "tube_od",
                "tube_id",
                "tube_length",
            ]
    
            missing = [
                key
                for key in required_geometry
                if key not in self.data.get("specs", {})
            ]
    
            if missing:
    
                raise ValueError(
                    "Rate mode requires fixed geometry. "
                    f"Missing: {missing}"
                )
    
            results = hx.rate()
    
        # ======================================================
        # INVALID MODE
        # ======================================================
    
        else:
    
            raise ValueError(
                f"Unsupported exchanger mode: {mode}"
            )
    
        # ======================================================
        # STORE RESULTS
        # ======================================================
    
        self._results = HeatExchangerResults(results)
    
        return self._results

    def summary(self):
        if not self._results:
            return None
        return self._results.summary()
    def results(self):
        """Return design results"""
        if not hasattr(self, "_results"):
            raise RuntimeError("Run the model first using hx.run()")
        return self._results
