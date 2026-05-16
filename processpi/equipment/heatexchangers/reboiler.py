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

    def _estimate_circulation_ratio(self, results: Dict[str, Any]) -> float:
        duty_kw = float(results.get("Q", 0.0))
        area = max(float(results.get("Area", 1.0)), 1e-6)
        base = 3.0 + 0.002 * duty_kw + 0.01 * area
        if self.reboiler_type == "vertical_thermosyphon":
            base *= 1.2
        elif self.reboiler_type == "horizontal_thermosyphon":
            base *= 1.05
        return max(2.0, min(base, 12.0))

    def _circulation_factor(self) -> float:
        factors = {
            "kettle": 1.00,
            "horizontal_thermosyphon": 1.15,
            "vertical_thermosyphon": 1.30,
        }
        return factors.get(self.reboiler_type, 1.00)

    def _calculate_htc(self, dimless: Dict[str, float], geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float], **kwargs: Any):
        h_tube, h_shell = super()._calculate_htc(dimless, geometry, hot, cold)
        boost = self._circulation_factor()
        if self.boiling_side == "tube":
            h_tube *= boost
        else:
            h_shell *= boost
        return h_tube, h_shell

    def _calculate_pressure_drop(
        self,
        geometry: Dict[str, float],
        hot: Dict[str, float],
        cold: Dict[str, float],
        shell_velocity: float | None = None,
        tube_velocity: float | None = None,
        **kwargs: Any,
    ):
        shell_velocity = (
            shell_velocity
            if shell_velocity is not None
            else float(kwargs.get("shell_velocity", 0.0))
        )
        tube_velocity = (
            tube_velocity
            if tube_velocity is not None
            else float(kwargs.get("tube_velocity", 0.0))
        )
        kwargs.setdefault("shell_passes", int(kwargs.get("shell_passes", 1)))
        kwargs.setdefault("tube_passes", int(kwargs.get("tube_passes", 1)))
        _shell_diameter = kwargs.get("shell_diameter")
        return super()._calculate_pressure_drop(
            geometry=geometry,
            hot=hot,
            cold=cold,
            shell_velocity=shell_velocity,
            tube_velocity=tube_velocity,
            **kwargs,
        )

    def _decorate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        results = super()._decorate_results(results)
        circulation_ratio = self._estimate_circulation_ratio(results)
        if circulation_ratio < 3.0:
            self._warn_with_category("HYDRAULIC_WARNING", "Low estimated circulation ratio for reboiler")
        results.update({
            "hx_type": "reboiler",
            "service": "reboiler",
            "reboiler_type": self.reboiler_type,
            "circulation_factor": self._circulation_factor(),
            "circulation_ratio": circulation_ratio,
            "warning_details": [{"category": (w.split("]",1)[0][1:] if w.startswith("[") and "]" in w else "GENERAL_WARNING"), "message": (w.split("]",1)[1].strip() if w.startswith("[") and "]" in w else w)} for w in list(dict.fromkeys([*results.get("warnings", []), *self._warnings]))],
        })
        return results

    def design(self):
        return self._decorate_results(super().design())

    def rate(self):
        return self._decorate_results(super().rate())
