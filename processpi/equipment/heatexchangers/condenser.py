from __future__ import annotations

from typing import Any, Dict

from processpi.calculations.heat_transfer.hx_kern import CondensationHTC, LatentDuty

from .shell_and_tube import ShellAndTubeHX


class CondenserHX(ShellAndTubeHX):
    """Production-oriented shell-and-tube condenser with phase-change safeguards."""

    def __init__(self, *args: Any, method: str = "kern", **kwargs: Any):
        super().__init__(*args, method=method, **kwargs)
        self.service_type = "condenser"
        self.orientation = str(self.specs.get("orientation", "horizontal")).lower()
        self.condensing_side = str(self.specs.get("condensing_side", "shell")).lower()
        self.condensation_mode = str(self.specs.get("condensation_mode", "total")).lower()

    def _calculate_heat_duty(self, hot: Dict[str, float], cold: Dict[str, float]):
        latent_heat = self.specs.get("latent_heat")
        if latent_heat is None:
            raise ValueError("Condenser requires latent_heat for condensation service")

        vapor_fraction = float(self.specs.get("vapor_fraction_condensed", 1.0 if self.condensation_mode == "total" else 0.5))
        vapor_fraction = max(0.05, min(vapor_fraction, 1.0))

        q_watts = LatentDuty(m_dot=hot["m_dot"] * vapor_fraction, latent_heat=latent_heat).calculate().to("W").value
        th_in = hot["t_k"]
        tc_in = cold["t_k"]

        # Near-isothermal condensing side temperature
        th_out = th_in - float(self.specs.get("subcooling", 0.0))
        tc_out = tc_in + q_watts / max(cold["m_dot"] * cold["cp"] * 1000.0, 1e-12)

        if tc_out >= th_in:
            self._warn("Condenser cold outlet approaches/exceeds condensing temperature; clipping to feasible approach")
            tc_out = th_in - 1.0

        return q_watts, th_out, tc_out

    def _calculate_ft(self, *args: Any, **kwargs: Any) -> float:
        # Phase change service: bypass standard Ft correction.
        return 1.0

    def _calculate_condensation_htc(self, hot: Dict[str, float], geometry: Dict[str, float]) -> float:
        vapor_density = max(hot.get("density", 1.0), 0.1)
        liquid_density = max(float(self.specs.get("condensate_density", vapor_density * 50.0)), vapor_density + 1.0)
        liquid_viscosity = max(float(self.specs.get("condensate_viscosity", 3e-4)), 1e-5)
        liquid_k = max(float(self.specs.get("condensate_k", 0.1)), 0.01)
        latent_heat = float(self.specs.get("latent_heat", 2.2e6))
        delta_t = max(float(self.specs.get("condensation_dT", 5.0)), 0.5)
        length = max(float(geometry.get("tube_length", 6.0)), 0.5)

        h_base = CondensationHTC(
            rho_l=liquid_density,
            rho_v=vapor_density,
            mu_l=liquid_viscosity,
            k_l=liquid_k,
            h_fg=latent_heat,
            delta_t=delta_t,
            length=length,
        ).calculate().to("W/m2K").value

        orientation_factor = 1.0 if self.orientation == "vertical" else 0.85
        side_factor = 0.9 if self.condensing_side == "tube" else 1.0
        h_cond = h_base * orientation_factor * side_factor
        return max(1200.0, min(h_cond, 20000.0))

    def _calculate_htc(self, dimless: Dict[str, float], geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float]):
        h_tube, h_shell = super()._calculate_htc(dimless, geometry, hot, cold)
        h_cond = self._calculate_condensation_htc(hot, geometry)

        if self.condensing_side == "tube":
            h_tube = h_cond
        else:
            h_shell = h_cond
        return h_tube, h_shell

    def _calculate_pressure_drop(self, hot: Dict[str, float], cold: Dict[str, float], geometry: Dict[str, float], tube_passes: int, tube_count: int):
        tube_dp, shell_dp = super()._calculate_pressure_drop(hot, cold, geometry, tube_passes, tube_count)
        if self.orientation == "vertical":
            static_head = float(self.specs.get("condensate_density", 850.0)) * 9.81 * max(float(geometry.get("tube_length", 6.0)), 0.0)
            if self.condensing_side == "tube":
                tube_dp += static_head
            else:
                shell_dp += static_head
        return tube_dp, shell_dp

    def _decorate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        results.update({
            "hx_type": "condenser",
            "service": self.condensation_mode + "_condenser",
            "phase_change": True,
            "orientation": self.orientation,
            "condensing_side": self.condensing_side,
            "convergence_status": results.get("status", "OK"),
            "warnings": list(dict.fromkeys([*results.get("warnings", []), *self._warnings])),
        })
        return results

    def design(self):
        return self._decorate_results(super().design())

    def rate(self):
        return self._decorate_results(super().rate())
