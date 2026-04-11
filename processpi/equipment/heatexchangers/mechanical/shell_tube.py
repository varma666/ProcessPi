"""
Structured Shell-and-Tube Heat Exchanger design workflow.

Primary workflow: Kern method (stepwise)
Shell-side refinement: Bell-Delaware correction factors
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from ....streams.material import MaterialStream
from ....units import Diameter, Length, Pressure, ThermalConductivity
from ..base import HeatExchanger


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
_DEFAULT_WALL_K = 16.0
_DEFAULT_FOULING_TUBE = 1e-4
_DEFAULT_FOULING_SHELL = 2e-4
_DEFAULT_ROUGHNESS = 1.5e-5
_DEFAULT_TOL = 1e-3
_DEFAULT_MAX_ITERS = 25

_DEFAULT_U_RANGES = {
    "liquid_liquid": (300.0, 800.0),
    "water_water": (500.0, 1000.0),
    "condenser": (1000.0, 3000.0),
}

# limits
_TUBE_V_LIQ = (1.0, 2.0)
_TUBE_V_WATER = (1.5, 2.5)
_SHELL_V_LIQ = (0.3, 1.0)
_DP_LIQ_MAX = 70_000.0
_DP_LIQ_MIN_GUIDE = 35_000.0


def pack_tubes_in_shell(
    D_shell: float,
    D_tube: float,
    pitch: float,
    layout: str = "triangular",
) -> Tuple[List[Tuple[float, float]], int]:
    """
    Backward-compatible tube packing helper used by other modules.
    Returns (centers, count) with a conservative geometric estimate.
    """
    _ = pitch
    factor = 0.87 if layout.lower().startswith("tri") else 1.0
    count = max(1, int((D_shell / max(D_tube, 1e-9)) ** 2 * factor * 0.55))
    return [], count


@dataclass
class ShellTubeState:
    # core thermal
    Q_W: float = 0.0
    U_assumed: float = 500.0
    U_calculated: float = 500.0
    Ft: float = 1.0
    LMTD: float = 1.0
    A_required_m2: float = 1.0

    # geometry
    tube_od_m: float = 0.01905
    tube_id_m: float = 0.016
    tube_length_m: float = 4.0
    tube_layout: str = "triangular"
    tube_pitch_m: float = 0.0238
    tube_passes: int = 2
    n_tubes: int = 50
    shell_diameter_m: float = 0.4
    baffle_spacing_m: float = 0.1

    # fluid assignment
    tube_side: str = "hot"
    shell_side: str = "cold"

    # properties
    rho_t: float = 1000.0
    mu_t: float = 1e-3
    cp_t: float = 4180.0
    k_t: float = 0.6

    rho_s: float = 1000.0
    mu_s: float = 1e-3
    cp_s: float = 4180.0
    k_s: float = 0.6

    # transport/hydraulic
    velocity_tube: float = 0.0
    velocity_shell: float = 0.0
    Re_tube: float = 0.0
    Re_shell: float = 0.0
    h_tube: float = 0.0
    h_shell_ideal: float = 0.0
    h_shell_corrected: float = 0.0

    # Bell-Delaware factors
    J_c: float = 1.0
    J_l: float = 1.0
    J_b: float = 1.0
    J_r: float = 1.0
    J_s: float = 1.0

    # pressure drop
    dp_tube: float = 0.0
    dp_shell: float = 0.0

    # convergence/health
    converged: bool = False
    iterations: int = 0
    warnings: List[str] = field(default_factory=list)


class ShellAndTubeDesigner:
    def __init__(
        self,
        hx: HeatExchanger,
        *,
        tube_nominal: Optional[Diameter] = None,
        tube_schedule: Optional[str] = None,
        shell_do: Optional[Length] = None,
        tube_layout: str = "triangular",
        pitch_factor: float = 1.25,
        tube_passes_options: Optional[List[int]] = None,
        pass_layout: Optional[str] = None,
        arrangement: str = "counterflow",
        baffle_spacing: Optional[Length] = None,
        target_dp_tube: Optional[Pressure] = None,
        target_dp_shell: Optional[Pressure] = None,
        wall_k: Union[float, ThermalConductivity] = _DEFAULT_WALL_K,
        roughness: float = _DEFAULT_ROUGHNESS,
        fouling_tube: float = _DEFAULT_FOULING_TUBE,
        fouling_shell: float = _DEFAULT_FOULING_SHELL,
        max_iters: int = _DEFAULT_MAX_ITERS,
        tol: float = _DEFAULT_TOL,
        tube_side_hot: Optional[bool] = None,
    ):
        self.hx = hx
        self.parms = self._get_parms(hx)

        self.tube_nominal = tube_nominal
        self.tube_schedule = tube_schedule
        self.shell_do = shell_do
        self.tube_layout = tube_layout
        self.pitch_factor = pitch_factor
        self.tube_passes_options = tube_passes_options or [1, 2]
        self.pass_layout = pass_layout
        self.arrangement = arrangement
        self.baffle_spacing_input = baffle_spacing
        self.target_dp_tube = target_dp_tube.to("Pa").value if target_dp_tube else None
        self.target_dp_shell = target_dp_shell.to("Pa").value if target_dp_shell else None

        self.wall_k = wall_k.value if hasattr(wall_k, "value") else float(wall_k)
        self.roughness = roughness
        self.fouling_tube = fouling_tube
        self.fouling_shell = fouling_shell
        self.max_iters = max_iters
        self.tol = tol
        self.tube_side_hot = tube_side_hot

        self.state = ShellTubeState()

    def design(self) -> Dict[str, Any]:
        self._kern_design()
        return self._step16_finalize()

    # ------------------------------------------------------------------
    # Kern workflow (mandatory step structure)
    # ------------------------------------------------------------------
    def _kern_design(self):
        self._step1_heat_duty()
        self._step2_properties()
        self._step3_assume_U()
        self._step4_passes()
        self._step5_LMTD()
        self._step6_area()
        self._step7_geometry_selection()
        self._step8_tube_count()
        self._step9_shell_diameter()
        self._step10_tube_htc()
        self._step11_baffle_spacing()
        self._step12_shell_htc()
        self._step13_overall_U()
        self._step14_U_convergence()
        self._step15_pressure_drop_check()

    def _step1_heat_duty(self):
        th_in = self._val(self.parms.get("Hot in Temp"), "Th_in")
        th_out = self._val(self.parms.get("Hot out Temp"), "Th_out")
        tc_in = self._val(self.parms.get("Cold in Temp"), "Tc_in")
        tc_out = self._val(self.parms.get("Cold out Temp"), "Tc_out")
        m_hot = self._val(self.parms.get("m_hot"), "m_hot")
        m_cold = self._val(self.parms.get("m_cold"), "m_cold")
        cp_hot = self._val(self.parms.get("cP_hot"), "cp_hot")
        cp_cold = self._val(self.parms.get("cP_cold"), "cp_cold")

        q_hot = m_hot * cp_hot * (th_in - th_out)
        q_cold = m_cold * cp_cold * (tc_out - tc_in)
        self.state.Q_W = abs(0.5 * (q_hot + q_cold)) if q_hot and q_cold else abs(q_hot or q_cold)

    def _step2_properties(self):
        tube_stream, shell_stream = self._allocate_fluids()
        self.state.tube_side = "hot" if tube_stream is self.hx.hot_in else "cold"
        self.state.shell_side = "cold" if self.state.tube_side == "hot" else "hot"

        self.state.rho_t, self.state.mu_t, self.state.cp_t, self.state.k_t = self._stream_properties(tube_stream)
        self.state.rho_s, self.state.mu_s, self.state.cp_s, self.state.k_s = self._stream_properties(shell_stream)

    def _step3_assume_U(self):
        hot = self.hx.hot_in
        cold = self.hx.cold_in
        hot_name = getattr(getattr(hot, "component", None), "name", "").lower()
        cold_name = getattr(getattr(cold, "component", None), "name", "").lower()

        if "water" in hot_name and "water" in cold_name:
            lo, hi = _DEFAULT_U_RANGES["water_water"]
        elif "steam" in hot_name or "vapor" in hot_name:
            lo, hi = _DEFAULT_U_RANGES["condenser"]
        else:
            lo, hi = _DEFAULT_U_RANGES["liquid_liquid"]
        self.state.U_assumed = 0.5 * (lo + hi)

    def _step4_passes(self):
        self.state.tube_passes = 2 if 2 in self.tube_passes_options else self.tube_passes_options[0]

    def _step5_LMTD(self):
        th_in = self._val(self.parms.get("Hot in Temp"), "Th_in")
        th_out = self._val(self.parms.get("Hot out Temp"), "Th_out")
        tc_in = self._val(self.parms.get("Cold in Temp"), "Tc_in")
        tc_out = self._val(self.parms.get("Cold out Temp"), "Tc_out")

        d1 = th_in - tc_out
        d2 = th_out - tc_in
        if d1 <= 0 or d2 <= 0:
            self.state.LMTD = max(abs(d1), abs(d2), 1e-6)
            self.state.warnings.append("Temperature cross detected; LMTD approximated.")
        elif abs(d1 - d2) < 1e-9:
            self.state.LMTD = d1
        else:
            self.state.LMTD = (d1 - d2) / math.log(d1 / d2)

        self.state.Ft = self._correction_factor_Ft()
        if self.state.Ft < 0.75:
            self.state.warnings.append("Ft is low; exchanger correction factor may be unacceptable.")

    def _step6_area(self):
        self.state.A_required_m2 = self.state.Q_W / max(self.state.U_assumed * self.state.LMTD * self.state.Ft, 1e-9)

    def _step7_geometry_selection(self):
        # keep same unit system and practical defaults
        self.state.tube_od_m = 0.01905
        self.state.tube_id_m = 0.016
        self.state.tube_layout = self.tube_layout
        self.state.tube_pitch_m = self.pitch_factor * self.state.tube_od_m
        self.state.tube_length_m = 4.0

    def _step8_tube_count(self):
        area_per_tube = math.pi * self.state.tube_od_m * self.state.tube_length_m
        self.state.n_tubes = max(1, math.ceil(self.state.A_required_m2 / max(area_per_tube, 1e-9)))

    def _step9_shell_diameter(self):
        # empirical style bundle estimate
        layout_factor = 0.87 if self.state.tube_layout.startswith("tri") else 1.0
        bundle = math.sqrt(self.state.n_tubes * (self.state.tube_pitch_m ** 2) / max(layout_factor, 1e-9))
        self.state.shell_diameter_m = max(0.15, 1.1 * bundle)
        if self.shell_do is not None:
            self.state.shell_diameter_m = self.shell_do.to("m").value

    def _step10_tube_htc(self):
        m_tube = self._tube_mass_flow()
        channels = max(1, self.state.n_tubes / max(self.state.tube_passes, 1))
        area_flow = channels * math.pi * (self.state.tube_id_m ** 2) / 4.0
        self.state.velocity_tube = m_tube / max(self.state.rho_t * area_flow, 1e-9)
        self.state.Re_tube = self.state.rho_t * self.state.velocity_tube * self.state.tube_id_m / max(self.state.mu_t, 1e-12)
        pr = self._pr(self.state.cp_t, self.state.mu_t, self.state.k_t)
        nu = self._nusselt_dittus_boelter(self.state.Re_tube, pr)
        self.state.h_tube = nu * self.state.k_t / max(self.state.tube_id_m, 1e-9)

    def _step11_baffle_spacing(self):
        if self.baffle_spacing_input is not None:
            self.state.baffle_spacing_m = self.baffle_spacing_input.to("m").value
        else:
            self.state.baffle_spacing_m = 0.3 * self.state.shell_diameter_m
        lo = 0.2 * self.state.shell_diameter_m
        hi = 0.5 * self.state.shell_diameter_m
        self.state.baffle_spacing_m = min(max(self.state.baffle_spacing_m, lo), hi)

    def _step12_shell_htc(self):
        h_ideal, re_shell, v_shell = self._shell_ideal_htc()
        self.state.h_shell_ideal = h_ideal
        self.state.Re_shell = re_shell
        self.state.velocity_shell = v_shell

        j_c, j_l, j_b, j_r, j_s = self._bell_delaware_factors(re_shell)
        self.state.J_c = j_c
        self.state.J_l = j_l
        self.state.J_b = j_b
        self.state.J_r = j_r
        self.state.J_s = j_s
        self.state.h_shell_corrected = h_ideal * j_c * j_l * j_b * j_r * j_s

    def _step13_overall_U(self):
        do = self.state.tube_od_m
        di = self.state.tube_id_m
        wall = math.log(do / di) * do / (2.0 * self.wall_k) if do > di else 0.0
        inv_u = (
            (1.0 / max(self.state.h_tube, 1e-9)) * (do / di)
            + self.fouling_tube
            + wall
            + self.fouling_shell
            + 1.0 / max(self.state.h_shell_corrected, 1e-9)
        )
        self.state.U_calculated = 1.0 / max(inv_u, 1e-12)

    def _step14_U_convergence(self):
        self.state.converged = False
        for i in range(1, self.max_iters + 1):
            self.state.iterations = i
            self._step6_area()
            self._step8_tube_count()
            self._step9_shell_diameter()
            self._step10_tube_htc()
            self._step11_baffle_spacing()
            self._step12_shell_htc()
            self._step13_overall_U()

            err = abs(self.state.U_calculated - self.state.U_assumed) / max(self.state.U_assumed, 1e-9)
            if err < 0.3:
                self.state.converged = True
                return

            self.state.U_assumed = 0.6 * self.state.U_assumed + 0.4 * self.state.U_calculated
            self._adjust_design_on_constraint_failure()

    def _step15_pressure_drop_check(self):
        self.state.dp_tube = self._tube_pressure_drop()
        self.state.dp_shell = self._shell_pressure_drop()

        # warnings / constraints
        self._velocity_warnings()

        if self.state.dp_tube > _DP_LIQ_MAX:
            self.state.warnings.append("Tube-side pressure drop exceeds 70 kPa limit.")
        elif self.state.dp_tube > _DP_LIQ_MIN_GUIDE:
            self.state.warnings.append("Tube-side pressure drop above preferred 35 kPa guidance.")

        if self.state.dp_shell > _DP_LIQ_MAX:
            self.state.warnings.append("Shell-side pressure drop exceeds 70 kPa limit.")
        elif self.state.dp_shell > _DP_LIQ_MIN_GUIDE:
            self.state.warnings.append("Shell-side pressure drop above preferred 35 kPa guidance.")

        if self.target_dp_tube is not None and self.state.dp_tube > self.target_dp_tube:
            self.state.warnings.append("Tube-side ΔP exceeds user target.")
        if self.target_dp_shell is not None and self.state.dp_shell > self.target_dp_shell:
            self.state.warnings.append("Shell-side ΔP exceeds user target.")

        if self.state.tube_length_m > 12.0:
            self.state.warnings.append("Tube length is high (>12 m), may be impractical.")

    def _step16_finalize(self) -> Dict[str, Any]:
        results = {
            "Q_W": self.state.Q_W,
            "U_W_m2K": self.state.U_calculated,
            "A_required_m2": self.state.A_required_m2,
            "L_tube_m": self.state.tube_length_m,
            "N_tubes": self.state.n_tubes,
            "Re_tube": self.state.Re_tube,
            "Re_shell": self.state.Re_shell,
            "dp_tube": self.state.dp_tube,
            "dp_shell": self.state.dp_shell,
            "velocity_tube": self.state.velocity_tube,
            "velocity_shell": self.state.velocity_shell,
            "converged": self.state.converged,
            "tube_side": self.state.tube_side,
            "shell_side": self.state.shell_side,
            "Ft": self.state.Ft,
            "tube_passes": self.state.tube_passes,
            "shell_diameter_m": self.state.shell_diameter_m,
            "tube_od_m": self.state.tube_od_m,
            "tube_id_m": self.state.tube_id_m,
            "baffle_spacing_m": self.state.baffle_spacing_m,
            "bell_delaware": {
                "J_c": self.state.J_c,
                "J_l": self.state.J_l,
                "J_b": self.state.J_b,
                "J_r": self.state.J_r,
                "J_s": self.state.J_s,
                "h_shell_ideal": self.state.h_shell_ideal,
                "h_shell_corrected": self.state.h_shell_corrected,
            },
            "warnings": self.state.warnings,
            "iterations": self.state.iterations,
        }
        self.hx.design_results = results
        return results

    # ------------------------------------------------------------------
    # Engineering helper functions
    # ------------------------------------------------------------------
    @staticmethod
    def _get_parms(hx: HeatExchanger) -> Dict[str, Any]:
        if hx.simulated_params is None:
            raise ValueError("Heat exchanger has not been simulated yet (simulated_params missing).")
        return hx.simulated_params

    @staticmethod
    def _val(v, name: str):
        if v is None:
            raise ValueError(f"{name} is required")
        if hasattr(v, "value"):
            return float(v.value)
        return float(v)

    @staticmethod
    def _pr(cp: float, mu: float, k: float) -> float:
        return cp * mu / max(k, 1e-12)

    @staticmethod
    def _nusselt_dittus_boelter(re: float, pr: float) -> float:
        if re < 2300:
            return 3.66
        return 0.023 * (re ** 0.8) * (pr ** 0.4)

    def _stream_properties(self, stream: MaterialStream) -> Tuple[float, float, float, float]:
        # Mean-temperature intent retained; uses stream/component current state in current API.
        rho = getattr(stream, "density", None)
        mu = getattr(getattr(stream, "component", None), "viscosity", None)
        cp = getattr(stream, "specific_heat", None)
        k = getattr(getattr(stream, "component", None), "thermal_conductivity", None)

        rho_v = rho.to("kg/m3").value if hasattr(rho, "to") else 1000.0
        mu_v = mu().to("Pa·s").value if callable(mu) else 1e-3
        cp_v = cp.to("J/kgK").value if hasattr(cp, "to") else 4180.0
        k_v = k().to("W/mK").value if callable(k) else 0.6
        return float(rho_v), float(mu_v), float(cp_v), float(k_v)

    def _allocate_fluids(self) -> Tuple[MaterialStream, MaterialStream]:
        hot = self.hx.hot_in
        cold = self.hx.cold_in
        if hot is None or cold is None:
            raise ValueError("Both hot_in and cold_in streams are required.")

        if self.tube_side_hot is not None:
            return (hot, cold) if self.tube_side_hot else (cold, hot)

        hot_comp = getattr(hot, "component", None)
        cold_comp = getattr(cold, "component", None)
        hot_phase = hot.phase or (hot_comp.phase.value if hot_comp is not None and hasattr(hot_comp, "phase") else "liquid")
        cold_phase = cold.phase or (cold_comp.phase.value if cold_comp is not None and hasattr(cold_comp, "phase") else "liquid")

        # Tube side if corrosive/high-pressure/fouling/hot; shell side for condensing vapor/viscous/low flow.
        # Practical auto-rule implemented via phase + viscosity heuristics.
        if "gas" in str(hot_phase).lower() or "vapor" in str(hot_phase).lower():
            return cold, hot

        mu_hot = hot_comp.viscosity().to("Pa·s").value if hot_comp is not None else 1e-3
        mu_cold = cold_comp.viscosity().to("Pa·s").value if cold_comp is not None else 1e-3
        if mu_hot > mu_cold * 2.0:
            return cold, hot

        return hot, cold

    def _tube_mass_flow(self) -> float:
        return self._val(self.parms["m_hot"], "m_hot") if self.state.tube_side == "hot" else self._val(self.parms["m_cold"], "m_cold")

    def _shell_mass_flow(self) -> float:
        return self._val(self.parms["m_cold"], "m_cold") if self.state.tube_side == "hot" else self._val(self.parms["m_hot"], "m_hot")

    def _correction_factor_Ft(self) -> float:
        # Step-wise Ft approximation based on arrangement + passes.
        base = 1.0 if self.arrangement.lower() == "counterflow" else 0.92
        pass_penalty = 0.95 if self.state.tube_passes == 2 else 1.0
        return max(0.5, min(1.0, base * pass_penalty))

    def _shell_ideal_htc(self) -> Tuple[float, float, float]:
        m_shell = self._shell_mass_flow()
        ds = self.state.shell_diameter_m
        do = self.state.tube_od_m
        pt = self.state.tube_pitch_m
        bs = self.state.baffle_spacing_m

        free_area = max(1e-6, ds * bs * (pt - do) / max(pt, 1e-9))
        g_shell = m_shell / free_area
        v_shell = g_shell / max(self.state.rho_s, 1e-12)
        de = max(1e-4, 1.1 * (pt - do))
        re_shell = g_shell * de / max(self.state.mu_s, 1e-12)
        pr_shell = self._pr(self.state.cp_s, self.state.mu_s, self.state.k_s)

        if re_shell < 100:
            nu_shell = 0.9 * (re_shell ** 0.4) * (pr_shell ** 0.33)
        else:
            nu_shell = 0.36 * (re_shell ** 0.55) * (pr_shell ** 0.33)
        h_ideal = nu_shell * self.state.k_s / max(de, 1e-9)
        return h_ideal, re_shell, v_shell

    def _bell_delaware_factors(self, re_shell: float) -> Tuple[float, float, float, float, float]:
        # baffle cut/configuration
        baffle_cut = 0.25
        j_c = 0.55 + 0.72 * (1.0 - baffle_cut)

        # leakage
        leak_frac = min(0.35, 0.02 + 0.15 * baffle_cut)
        j_l = math.exp(-1.33 * leak_frac)

        # bypass
        bypass_frac = min(0.4, 0.04 + 0.2 * (1.0 - self.state.n_tubes / max(self.state.n_tubes + 20, 1)))
        j_b = math.exp(-1.25 * bypass_frac)

        # laminar correction
        j_r = 1.0 if re_shell >= 100 else max(0.4, re_shell / 100.0)

        # unequal spacing correction
        j_s = max(0.7, min(1.0, self.state.baffle_spacing_m / max(0.3 * self.state.shell_diameter_m, 1e-9)))
        return j_c, j_l, j_b, j_r, j_s

    def _tube_pressure_drop(self) -> float:
        re = max(self.state.Re_tube, 1e-12)
        if re < 2300:
            f = 64.0 / re
        else:
            f = 0.3164 / (re ** 0.25)

        l_eff = self.state.tube_length_m * max(self.state.tube_passes, 1)
        dp = f * (l_eff / max(self.state.tube_id_m, 1e-9)) * 0.5 * self.state.rho_t * (self.state.velocity_tube ** 2)
        return dp

    def _shell_pressure_drop(self) -> float:
        re = max(self.state.Re_shell, 1e-12)
        if re < 2300:
            f = 64.0 / re
        else:
            f = 0.3164 / (re ** 0.25)

        n_baffles = max(1, int(self.state.tube_length_m / max(self.state.baffle_spacing_m, 1e-9)) - 1)
        dp_ideal = f * n_baffles * 0.5 * self.state.rho_s * (self.state.velocity_shell ** 2)
        return dp_ideal / max(self.state.J_l * self.state.J_b, 1e-6)

    def _velocity_warnings(self) -> None:
        tube_comp_name = getattr(getattr(self.hx.hot_in if self.state.tube_side == "hot" else self.hx.cold_in, "component", None), "name", "").lower()
        if "water" in tube_comp_name:
            vlo, vhi = _TUBE_V_WATER
        else:
            vlo, vhi = _TUBE_V_LIQ

        if not (vlo <= self.state.velocity_tube <= vhi):
            self.state.warnings.append(f"Tube velocity {self.state.velocity_tube:.3f} m/s outside recommended {vlo}-{vhi} m/s.")

        svlo, svhi = _SHELL_V_LIQ
        if not (svlo <= self.state.velocity_shell <= svhi):
            self.state.warnings.append(f"Shell velocity {self.state.velocity_shell:.3f} m/s outside recommended {svlo}-{svhi} m/s.")

        if self.state.Re_tube < 4000:
            self.state.warnings.append("Tube-side Reynolds number is low; heat transfer may be poor.")
        if self.state.Re_shell < 2000:
            self.state.warnings.append("Shell-side Reynolds number is low; Bell-Delaware correction may be less reliable.")

    def _adjust_design_on_constraint_failure(self) -> None:
        # iterative design adjustments requested
        self.state.tube_length_m = min(12.0, self.state.tube_length_m * 1.05)
        self.state.shell_diameter_m *= 1.03
        self.state.n_tubes = int(math.ceil(self.state.n_tubes * 1.03))
        if self.state.velocity_tube > _TUBE_V_WATER[1] and self.state.tube_passes > 1:
            self.state.tube_passes = max(1, self.state.tube_passes - 1)


# ---------------------------------------------------------------------------
# Backward-compatible public entrypoint
# ---------------------------------------------------------------------------
def design_shelltube(hx: HeatExchanger, **kwargs) -> Dict[str, Any]:
    designer = ShellAndTubeDesigner(hx, **kwargs)
    return designer.design()
