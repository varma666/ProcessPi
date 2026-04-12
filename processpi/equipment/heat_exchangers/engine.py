from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from .base import HeatExchanger
from .condenser import CondenserHX
from .double_pipe import DoublePipeHX
from .evaporator import EvaporatorHX
from .reboiler import ReboilerHX
from .shell_and_tube import ShellAndTubeHX


@dataclass
class HeatExchangerResults:
    results: Dict[str, Any]

    def summary(self) -> Dict[str, Any]:
        print("\n=== Heat Exchanger Summary ===")
        print(f"Type: {self.results.get('hx_type', 'N/A')}")
        print(f"Duty: {self.results.get('duty_W')}")
        print(f"Overall U: {self.results.get('overall_U_W_m2K')}")
        print(f"Required Area: {self.results.get('required_area_m2')}")
        return self.results

    def detailed_summary(self) -> Dict[str, Any]:
        print("\n=== Heat Exchanger Detailed Summary ===")
        for key, value in self.results.items():
            print(f"- {key}: {value}")
        return self.results


class HeatExchangerEngine:
    """Engine-style API for heat exchanger sizing and rating."""

    _model_map: Dict[str, Type[HeatExchanger]] = {
        "shell_and_tube": ShellAndTubeHX,
        "double_pipe": DoublePipeHX,
        "condenser": CondenserHX,
        "reboiler": ReboilerHX,
        "evaporator": EvaporatorHX,
    }

    def __init__(self, **kwargs: Any):
        self.data: Dict[str, Any] = {}
        self._results: Optional[HeatExchangerResults] = None
        if kwargs:
            self.fit(**kwargs)

    def fit(
        self,
        hx_type: Optional[str] = None,
        hot_fluid: Optional[Dict[str, Any]] = None,
        cold_fluid: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "HeatExchangerEngine":
        self.data = dict(kwargs)
        if hx_type is not None:
            self.data["hx_type"] = hx_type
        if hot_fluid is not None:
            self.data["hot_fluid"] = hot_fluid
        if cold_fluid is not None:
            self.data["cold_fluid"] = cold_fluid
        if config is not None:
            self.data["config"] = config

        alias_map = {
            "hx_type": ["type", "exchanger_type"],
            "hot_fluid": ["hot", "hot_stream"],
            "cold_fluid": ["cold", "cold_stream"],
            "config": ["settings", "params"],
        }
        for canonical, aliases in alias_map.items():
            if canonical not in self.data:
                for alias in aliases:
                    if alias in self.data:
                        self.data[canonical] = self.data[alias]
                        break

        self.data.setdefault("config", {})
        return self

    def run(self) -> HeatExchangerResults:
        hx_type = self.data.get("hx_type")
        if hx_type not in self._model_map:
            raise ValueError(f"Unknown heat exchanger type '{hx_type}'. Supported: {list(self._model_map)}")

        model_cls = self._model_map[hx_type]
        model = model_cls(
            hot_fluid=self.data.get("hot_fluid", {}),
            cold_fluid=self.data.get("cold_fluid", {}),
            config=self.data.get("config", {}),
        )
        self._results = HeatExchangerResults(model.design())
        return self._results

    def summary(self):
        if not self._results:
            print("No results available for summary.")
            return None
        return self._results.summary()
