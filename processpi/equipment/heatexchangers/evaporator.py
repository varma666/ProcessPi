from __future__ import annotations

from typing import Any, Dict

from processpi.calculations.heat_transfer.hx_kern import BoilingHTC, LatentDuty

from .shell_and_tube import ShellAndTubeHX


class EvaporatorHX(ShellAndTubeHX):
    def __init__(self, *args: Any, method: str = "kern", **kwargs: Any):
        super().__init__(*args, method=method, **kwargs)
        self.service_type = "evaporator"
        self.orientation = str(self.specs.get("orientation", "horizontal")).lower()
        self.boiling_side = str(self.specs.get("boiling_side", "shell")).lower()
        self.design_limits = {
            "max_shell_diameter": float(self.specs.get("max_shell_diameter", 2.0)),
            "max_tube_count": int(self.specs.get("max_tube_count", 5000)),
            "min_tube_velocity": float(self.specs.get("min_tube_velocity", 0.3)),
            "max_tube_velocity": float(self.specs.get("max_tube_velocity", 2.5)),
            "min_shell_velocity": float(self.specs.get("min_shell_velocity", 0.2)),
            "target_tube_velocity": float(self.specs.get("target_tube_velocity", 1.0)),
            "target_shell_velocity": float(self.specs.get("target_shell_velocity", 0.5)),
            "max_area": float(self.specs.get("max_area", 1000.0)),
        }

    def _calculate_heat_duty(self, hot: Dict[str, float], cold: Dict[str, float], **kwargs: Any):
        latent_heat = self.specs.get("latent_heat") or self._resolve_phase_change_latent_heat(hot, cold)
        if latent_heat is None:
            raise ValueError("Evaporator requires latent_heat or detectable phase-change service")
        q_watts = LatentDuty(m_dot=cold["m_dot"], latent_heat=latent_heat).calculate().to("W").value

        hot_latent = self._resolve_phase_change_latent_heat(hot, cold) if hot.get("phase") in {"vapor", "steam"} else None
        if hot_latent is not None:
            q_max = hot["m_dot"] * hot_latent
        else:
            q_max = hot["m_dot"] * hot["cp"] * 1000.0 * max(hot["t_k"] - cold["t_k"], 0.5)
        if q_watts > 0.98 * q_max:
            self._warn_with_category("FEASIBILITY_WARNING", "Requested evaporator duty exceeds hot-side available sensible heat; clipping to feasible duty")
            q_watts = 0.98 * q_max

        th_out = hot["t_k"] - q_watts / max(hot["m_dot"] * hot["cp"] * 1000.0, 1e-12)
        tc_out = cold["t_k"]  # near-isothermal boiling
        return q_watts, th_out, tc_out

    def _calculate_ft(self, *args: Any, **kwargs: Any) -> float:
        return 1.0

    def _calculate_boiling_htc(self, cold: Dict[str, float], q_flux: float) -> float:
        pressure = max(cold.get("p_bar", 1.0), 0.5)
        h_boil = BoilingHTC(heat_flux=max(q_flux, 1e3), pressure=pressure).calculate().to("W/m2K").value
        orientation_factor = 1.1 if self.orientation == "vertical" else 1.0
        return max(1500.0, min(h_boil * orientation_factor, 18000.0))

    def _calculate_htc(self, dimless: Dict[str, float], geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float], **kwargs: Any):
        h_tube, h_shell = super()._calculate_htc(dimless, geometry, hot, cold)
        q_flux = max(float(self.specs.get("Q", 1e6)) / max(geometry.get("area", 1.0), 1e-9), 1e3)
        h_boil = self._calculate_boiling_htc(cold, q_flux)

        if self.boiling_side == "tube":
            h_tube = h_boil
            h_shell = max(h_shell, 220.0)
        else:
            h_shell = h_boil
            h_tube = max(h_tube, 250.0)
        return h_tube, h_shell

    def _validate_design_constraints(self, results: Dict[str, Any]) -> None:
        limits = self.design_limits
        if results.get("Area", 0.0) > limits["max_area"]:
            self._warn_with_category("GEOMETRY_WARNING", "Area exceeds configured evaporator design limit")
        if results.get("tube_count", 0) > limits["max_tube_count"]:
            self._warn_with_category("GEOMETRY_WARNING", "Tube count exceeds configured evaporator design limit")
        if results.get("shell_diameter", 0.0) > limits["max_shell_diameter"]:
            self._warn_with_category("GEOMETRY_WARNING", "Shell diameter exceeds configured evaporator design limit")
        if results.get("tube_velocity", 0.0) < limits["min_tube_velocity"]:
            self._warn_with_category("HYDRAULIC_WARNING", "Tube velocity below recommended minimum; hydraulic collapse risk")
        if results.get("tube_velocity", 0.0) > limits["max_tube_velocity"]:
            self._warn_with_category("HYDRAULIC_WARNING", "Tube velocity above recommended maximum")
        if results.get("shell_velocity", 0.0) < limits["min_shell_velocity"]:
            self._warn_with_category("HYDRAULIC_WARNING", "Shell velocity below recommended minimum")
        if results.get("tube_velocity", 0.0) < limits["target_tube_velocity"]:
            self._warn_with_category("HYDRAULIC_WARNING", "Tube velocity below target tube velocity")
        if results.get("shell_velocity", 0.0) < limits["target_shell_velocity"]:
            self._warn_with_category("HYDRAULIC_WARNING", "Shell velocity below target shell velocity")

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
        shell_passes = int(kwargs.get("shell_passes", 1))
        tube_passes = int(kwargs.get("tube_passes", 1))
        _shell_diameter = kwargs.get("shell_diameter")

        tube_dp, shell_dp = super()._calculate_pressure_drop(
            geometry=geometry,
            hot=hot,
            cold=cold,
            shell_velocity=shell_velocity,
            tube_velocity=tube_velocity,
            shell_passes=shell_passes,
            tube_passes=tube_passes,
        )
        orientation = str(kwargs.get("orientation", self.orientation)).lower()
        _ = kwargs.get("shell_diameter")
        if orientation == "vertical":
            rho = cold.get("density", 900.0) if self.boiling_side == "tube" else hot.get("density", 900.0)
            static_head = rho * 9.81 * max(float(geometry.get("tube_length", 6.0)), 0.0)
            if self.boiling_side == "tube":
                tube_dp += static_head
            else:
                shell_dp += static_head
        return tube_dp, shell_dp

    def _decorate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_design_constraints(results)
        results.update({
            "hx_type": "evaporator",
            "service": "evaporator",
            "phase_change": True,
            "orientation": self.orientation,
            "boiling_side": self.boiling_side,
            "convergence_status": results.get("status", "OK"),
            "warnings": list(dict.fromkeys([*results.get("warnings", []), *self._warnings])),
            "warning_details": [{"category": (w.split("]",1)[0][1:] if w.startswith("[") and "]" in w else "GENERAL_WARNING"), "message": (w.split("]",1)[1].strip() if w.startswith("[") and "]" in w else w)} for w in list(dict.fromkeys([*results.get("warnings", []), *self._warnings]))],
        })
        return results

    def design(self):
        return self._decorate_results(super().design())

    def rate(self):
        return self._decorate_results(super().rate())
