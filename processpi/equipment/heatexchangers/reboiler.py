from __future__ import annotations

from typing import Any, Dict

from .evaporator import EvaporatorHX


class ReboilerHX(EvaporatorHX):
    """Shell-and-tube reboiler built from Evaporator phase-change architecture."""

    def __init__(self, *args: Any, method: str = "kern", **kwargs: Any):
        super().__init__(*args, method=method, **kwargs)
        self.service_type = "reboiler"
        self.reboiler_type = str(self.specs.get("reboiler_type", "kettle")).lower()
        self.orientation = str(self.specs.get("orientation", "horizontal")).lower()

    def _circulation_factor(self) -> float:
        factors = {
            "kettle": 1.00,
            "horizontal_thermosyphon": 1.15,
            "vertical_thermosyphon": 1.30,
        }
        return factors.get(self.reboiler_type, 1.00)

    def _calculate_htc(self, dimless: Dict[str, float], geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float]):
        h_tube, h_shell = super()._calculate_htc(dimless, geometry, hot, cold)
        boost = self._circulation_factor()
        if self.boiling_side == "tube":
            h_tube *= boost
        else:
            h_shell *= boost
        return h_tube, h_shell

    def _decorate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        results = super()._decorate_results(results)
        results.update({
            "hx_type": "reboiler",
            "service": "reboiler",
            "reboiler_type": self.reboiler_type,
            "circulation_factor": self._circulation_factor(),
        })
        return results

    def design(self):
        return self._decorate_results(super().design())

    def rate(self):
        return self._decorate_results(super().rate())
