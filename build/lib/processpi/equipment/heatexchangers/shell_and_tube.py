from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from processpi.calculations.heat_transfer import LMTD
from processpi.units.area import Area
from processpi.units.heat_flow import HeatFlow
from processpi.units.heat_transfer_coefficient import HeatTransferCoefficient
from processpi.units.length import Length
from processpi.units.pressure import Pressure
from processpi.units.velocity import Velocity
from processpi.calculations.fluids.friction_factor_colebrookwhite import ColebrookWhite
from processpi.calculations.heat_transfer.hx_kern import (
    ConvectiveH,
    DarcyDrop,
    DittusBoelter,
    KernShellNu,
    Reynolds,
)

from .base import HeatExchanger
from .standards import (
    DEFAULT_VELOCITY_RANGE,
    RECOMMENDED_VELOCITIES,
    CORROSION_SEVERITY_DATABASE,
    FOULING_FACTOR_DATABASE,
    STANDARD_TUBE_COUNT_TABLES,
    get_u_range,
    get_velocity_range,
    select_tube_configuration,
    tube_length_select,
    get_fouling_factor,
)

# Below this tolerance R is treated as exactly 1, where the 1/(R-1) factor of the
# Bowman correction factor is a removable 0/0 singularity and the analytic limit
# has to be used instead.
_R_UNITY_TOL = 1e-6

# F is genuinely undefined, not merely hard to compute, when a temperature cross
# makes the configuration infeasible: the Bowman log arguments turn non-positive
# and math.sqrt/math.log raise. Callers such as _adjust_passes read F = 0.0 as
# "this configuration is not usable, try more shell passes", so only these math
# failures are converted to 0.0. Anything else is a programming error and must
# propagate instead of being silently swallowed.
_FT_MATH_ERRORS = (ValueError, ZeroDivisionError, OverflowError)

# Dittus-Boelter exponent on Pr: 0.4 when the fluid is heated, 0.3 when it is
# cooled (Dittus and Boelter 1930; Incropera and DeWitt, Fundamentals of Heat and
# Mass Transfer, Eq. 8.60).
_DITTUS_BOELTER_N_HEATED = 0.4
_DITTUS_BOELTER_N_COOLED = 0.3

# Sieder-Tate viscosity correction exponent, phi = (mu / mu_w)^0.14 (Sieder and
# Tate 1936), as it enters Kern's shell-side Nusselt correlation and Kern's
# shell- and tube-side pressure drops (Kern 1950).
_SIEDER_TATE_EXPONENT = 0.14

# Tube-side laminar/turbulent switch for the friction factor, the value the code
# has always used; Kern (1950) takes tube flow as laminar below Re = 2100.
_TUBE_LAMINAR_RE = 2100.0

# Shell Reynolds range over which the Kern shell-side friction factor fit
# f = exp(0.576 - 0.19 ln Re) was checked against Kern's chart; see
# `_kern_shell_pressure_drop`.
_KERN_SHELL_F_RE_MIN = 200.0
_KERN_SHELL_F_RE_MAX = 1.0e6

# Bundle diameter constants K1, n1 in Db = do (Nt / K1)^(1/n1), keyed by the
# number of tube passes, for a tube pitch of 1.25 do. R. K. Sinnott, Coulson and
# Richardson's Chemical Engineering Vol. 6, Chemical Engineering Design, 4th ed.
# (Elsevier, 2005), Eq. 12.3 and Table 12.4.
_BUNDLE_CONSTANTS = {
    "triangular": {
        1: (0.319, 2.142),
        2: (0.249, 2.207),
        4: (0.175, 2.285),
        6: (0.0743, 2.499),
        8: (0.0365, 2.675),
    },
    "square": {
        1: (0.215, 2.207),
        2: (0.156, 2.291),
        4: (0.158, 2.263),
        6: (0.0402, 2.617),
        8: (0.0331, 2.643),
    },
}


class ShellAndTubeHX(HeatExchanger):
    # Which stream the model puts in the tubes regardless of the fluid-assignment
    # scoring, or None to let the scoring (or force_hot_in_tubes /
    # force_cold_in_tubes) decide. The phase-change subclasses pin it.
    _FIXED_TUBE_SIDE: str | None = None

    def __init__(self, *args: Any, method: str = "kern", **kwargs: Any):
        self.method = method.lower()
        if self.method not in {"kern", "bell_delaware"}:
            raise ValueError("method must be 'kern' or 'bell_delaware'")
        super().__init__(*args, **kwargs)
        # "hot" or "cold": the stream in the tubes. `_assign_fluids_to_sides`
        # resolves it at the start of design() and rate(); until then the
        # routines see the hot stream in the tubes, the arrangement the model
        # always used before the assignment drove it.
        self._tube_side = "hot"
        fixed_keys = ["tube_length", "tube_od", "tube_id", "tube_pitch", "tube_passes", "shell_passes", "shell_diameter", "tube_count", "tube_layout", "baffle_spacing"]
        self.fixed_geometry = {k: (self.specs.get(k) is not None) for k in fixed_keys}
        self._load_standard_tables()

    def _assume_u(self, hot: Dict[str, float], cold: Dict[str, float]) -> float:
        if self.specs.get("U") is not None:
            return self._safe_float(self.specs["U"].to("W/m2K"), "U")
        hot_type = getattr(self.hot_in.component, "hx_type", "generic")
        cold_type = getattr(self.cold_in.component, "hx_type", "generic")
        service_type = getattr(self, "service_type", "heat_exchanger")
        #self._debug(hot_type, cold_type, service_type)
        u_range = get_u_range("shell_and_tube", service_type, hot_type, cold_type)
        if u_range:
            u_min, u_max = u_range
            #self._debug(f"Assuming overall heat transfer coefficient U = {u_min}-{u_max} W/m2K based on service and fluids")
            return 0.5 * (u_min + u_max)
        return 300.0

    def _validate_inputs(self, hot: Dict[str, float], cold: Dict[str, float]) -> None:
        required = ["cp", "density", "viscosity", "k", "m_dot", "t_k"]
        missing: List[str] = []
        for side_name, props in (("hot", hot), ("cold", cold)):
            for key in required:
                val = props.get(key)
                self._debug(f"Side name {side_name}, {key} : {val}")
                if val is None or val <= 0:
                    
                    missing.append(f"{side_name}.{key}")
        if missing:
            raise ValueError(f"Missing or invalid stream properties for shell-and-tube design: {', '.join(missing)}")

    def _calculate_heat_duty(self, hot: Dict[str, float], cold: Dict[str, float]) -> Tuple[float, float, float]:
        q_watts = self.heat_duty(hot, cold)
        th_in = hot["t_k"]
        tc_in = cold["t_k"]
        #self._debug(f"Hot Cp: {hot["cp"]} Cold Cp {cold["cp"]}")
        # Both outlets follow from the duty and the side energy balances. The old
        # code kept a supplied outlet only when `.to("C")` compared equal to 25,
        # which cannot happen, so a supplied outlet was always dropped in silence.
        # It is honoured as a check instead: the balance decides, and a value that
        # disagrees with it is reported rather than swallowed.
        th_out = th_in - (q_watts / max(hot["m_dot"] * hot["cp"], 1e-9))
        tc_out = tc_in + (q_watts / max(cold["m_dot"] * cold["cp"], 1e-9))

        self._check_specified_outlet(self.hot_out, th_out, "hot")
        self._check_specified_outlet(self.cold_out, tc_out, "cold")

        return q_watts, th_out, tc_out

    def _check_specified_outlet(self, stream, t_balance_k: float, side: str) -> None:
        """
        Warn when a user-supplied outlet temperature disagrees with the energy
        balance, which is what the design is actually built on.

        Args:
            stream: The outlet MaterialStream, or None.
            t_balance_k (float): Outlet temperature from the energy balance [K].
            side (str): "hot" or "cold", for the message.
        """
        if stream is None or getattr(stream, "temperature", None) is None:
            return
        # A stream built without a temperature carries its component's
        # temperature object (25 C by default); that is not an outlet the user
        # specified, so there is nothing to check.
        component = getattr(stream, "component", None)
        if component is not None and stream.temperature is getattr(component, "temperature", None):
            return

        t_specified = self._safe_float(stream.temperature.to("K"), f"{side}_out.temperature")
        if abs(t_specified - t_balance_k) > 0.5:
            self._warn_with_category(
                "BALANCE_WARNING",
                f"Specified {side} outlet {t_specified:.2f} K disagrees with the "
                f"energy balance {t_balance_k:.2f} K; the balance value was used",
            )

    def _calculate_lmtd(self, hot: Dict[str, float], cold: Dict[str, float], th_out: float, tc_out: float) -> float:
        eps = 1e-3
        dt1 = hot["t_k"] - tc_out
        dt2 = th_out - cold["t_k"]
        phase_change_service = str(getattr(self, "service_type", "")).lower() in {"condenser", "reboiler", "evaporator"}

        if phase_change_service:
            if dt1 <= eps:
                self._warn_with_category("FEASIBILITY_WARNING", "Phase-change LMTD stabilization applied on terminal dT1")
                dt1 = eps
            if dt2 <= eps:
                self._warn_with_category("FEASIBILITY_WARNING", "Phase-change LMTD stabilization applied on terminal dT2")
                dt2 = eps
            if abs(dt1 - dt2) < eps:
                self._warn_with_category("FEASIBILITY_WARNING", "Near-isothermal phase-change exchanger stabilized")
                return 0.5 * (dt1 + dt2)
            return LMTD(dT1=dt1, dT2=dt2).calculate()

        return self.lmtd(hot["t_k"], th_out, cold["t_k"], tc_out)

    def _safe_log_ratio(self, numerator: float, denominator: float) -> float:
        if numerator <= 0.0 or denominator <= 0.0:
            raise ValueError("Log ratio arguments must be positive")
        return math.log(numerator / denominator)

    def _ft_1shell(self, r: float, s: float) -> float:
        try:
            if abs(r - 1.0) < _R_UNITY_TOL:
                # R = 1 limit (balanced duty). L'Hopital on the 1/(R-1) factor gives
                #   F = S sqrt(2) / (1-S) / ln[(2 - S(2 - sqrt2)) / (2 - S(2 + sqrt2))]
                sqrt2 = math.sqrt(2.0)
                numerator = s * sqrt2
                denominator = (1.0 - s) * self._safe_log_ratio(
                    2.0 - s * (2.0 - sqrt2), 2.0 - s * (2.0 + sqrt2)
                )
                if abs(denominator) < 1e-12:
                    return 0.0
                return max(min(numerator / denominator, 1.0), 0.0)

            sqrt_term = math.sqrt(r**2 + 1.0)

            numerator = sqrt_term * self._safe_log_ratio(1.0 - s, 1.0 - r * s)

            den_a = 2.0 - s * (r + 1.0 - sqrt_term)
            den_b = 2.0 - s * (r + 1.0 + sqrt_term)
            denominator = (r - 1.0) * self._safe_log_ratio(den_a, den_b)
            if abs(denominator) < 1e-12:
                return 0.0

            ft = numerator / denominator
            return max(min(ft, 1.0), 0.0)
        except _FT_MATH_ERRORS:
            return 0.0

    def _ft_2shell(self, r: float, s: float) -> float:
        # Bowman, Mueller and Nagle (1940) expression for 2 shell passes and 4 or
        # more (a multiple of 4) tube passes, as tabulated in Perry's Chemical
        # Engineers' Handbook, 8th ed., Table 11-3:
        #   F = sqrt(R^2+1) / (2(R-1)) * ln[(1-S)/(1-RS)]
        #       / ln[(W + sqrt(R^2+1)) / (W - sqrt(R^2+1))]
        #   W = 2/S - 1 - R + (2/S) sqrt((1-S)(1-RS))
        try:
            if s <= 0.0:
                return 0.0
            if abs(r - 1.0) < _R_UNITY_TOL:
                # R = 1 limit (balanced duty). W collapses to 4/S - 4, and L'Hopital on
                # the 1/(2(R-1)) factor gives
                #   F = S sqrt(2) / (2(1-S)) / ln[(4 - S(4 - sqrt2)) / (4 - S(4 + sqrt2))]
                sqrt2 = math.sqrt(2.0)
                numerator = s * sqrt2
                denominator = 2.0 * (1.0 - s) * self._safe_log_ratio(
                    4.0 - s * (4.0 - sqrt2), 4.0 - s * (4.0 + sqrt2)
                )
                if abs(denominator) < 1e-12:
                    return 0.0
                return max(min(numerator / denominator, 1.0), 0.0)

            sqrt_term = math.sqrt(r**2 + 1.0)

            a_term = (2.0 / s) - 1.0 - r + (2.0 / s) * math.sqrt((1.0 - s) * (1.0 - r * s))
            numerator = sqrt_term * self._safe_log_ratio(1.0 - s, 1.0 - r * s)

            den_a = a_term + sqrt_term
            den_b = a_term - sqrt_term
            denominator = 2.0 * (r - 1.0) * self._safe_log_ratio(den_a, den_b)
            if abs(denominator) < 1e-12:
                return 0.0

            ft = numerator / denominator
            return max(min(ft, 1.0), 0.0)
        except _FT_MATH_ERRORS:
            return 0.0

    def _calculate_ft(self, hot: Dict[str, float], cold: Dict[str, float], th_out: float, tc_out: float,
                      shell_passes: int, tube_passes: int) -> float:
        th_in = hot["t_k"]
        tc_in = cold["t_k"]

        r = (th_in - th_out) / max(tc_out - tc_in, 1e-12)
        s = (tc_out - tc_in) / max(th_in - tc_in, 1e-12)
        self._debug(f"R: {r} S: {s}")
        if shell_passes == 1:
            return self._ft_1shell(r, s)
        if shell_passes == 2:
            return self._ft_2shell(r, s)
        return 0.0

    def _adjust_passes(self, hot: Dict[str, float], cold: Dict[str, float], th_out: float, tc_out: float) -> Tuple[int, int, float]:
        candidates = [
            (1, 2), (1, 4), (1, 6), (1, 8),
            (2, 4), (2, 6), (2, 8),
        ]
        if self.specs.get("shell_passes") is not None and self.specs.get("tube_passes") is not None:
            specified = (int(self.specs["shell_passes"]), int(self.specs["tube_passes"]))
            candidates = [specified] + [c for c in candidates if c != specified]

        best: Tuple[int, int, float] | None = None
        best_ft = 0.0
        for shell_passes, tube_passes in candidates:
            ft = self._calculate_ft(hot, cold, th_out, tc_out, shell_passes, tube_passes)
            self._debug(f"Passes (shell={shell_passes}, tube={tube_passes}) → Ft = {ft:.4f}")

            if ft > best_ft:
                best_ft = ft
                best = (shell_passes, tube_passes, ft)

            if ft >= 0.78:
                return shell_passes, tube_passes, ft

        warnings = getattr(self, "_warnings", [])
        warnings.append("No pass configuration satisfies Ft ≥ 0.78 → using multiple exchangers in series")
        self._warnings = warnings

        return best if best is not None else (1, 2, 0.0)

    def _calculate_area(self, q_watts: float, u_assumed: float, cltd: float) -> float:
        return q_watts / max(u_assumed * cltd, 1e-9)

    def _round_tube_count_to_passes(self, tube_count: int, tube_passes: int) -> int:
        return max(tube_passes, int(math.ceil(tube_count / max(tube_passes, 1)) * max(tube_passes, 1)))

    def _load_standard_tables(self) -> None:
        self._tube_count_tables = STANDARD_TUBE_COUNT_TABLES
        self._fouling_db = FOULING_FACTOR_DATABASE
        self._corrosion_db = CORROSION_SEVERITY_DATABASE

    def _get_standard_layout(self) -> str:
        return str(self.specs.get("tube_layout", "triangular")).lower()

    def _shell_equivalent_diameter(
        self,
        tube_pitch: float,
        tube_od: float,
        layout: str | None = None,
    ) -> float:
        """
        Kern shell-side equivalent diameter for the bundle layout.

        Square pitch:       De = 4 (Pt^2 - pi do^2 / 4) / (pi do)
        Triangular pitch:   De = 4 (sqrt(3) Pt^2 / 4 - pi do^2 / 8) / (pi do / 2)

        Args:
            tube_pitch (float): Tube pitch [m].
            tube_od (float): Tube outside diameter [m].
            layout (str | None): "triangular" or "square"; the configured layout
                when omitted.

        Returns:
            float: Equivalent diameter [m].
        """
        layout = (layout or self._get_standard_layout()).lower()
        pitch = max(tube_pitch, 1e-9)
        od = max(tube_od, 1e-9)

        if layout.startswith("squ") or layout.startswith("rot"):
            free_area = pitch ** 2 - math.pi * od ** 2 / 4.0
            wetted = math.pi * od
        else:
            # 60 degree triangular pitch: half a pitch triangle per tube.
            free_area = math.sqrt(3.0) / 4.0 * pitch ** 2 - math.pi * od ** 2 / 8.0
            wetted = math.pi * od / 2.0

        return max(4.0 * free_area / max(wetted, 1e-12), 1e-6)

    def _shell_crossflow_area(
        self,
        shell_diameter: float,
        baffle_spacing: float,
        tube_pitch: float,
        tube_od: float,
    ) -> float:
        """
        Kern shell-side cross-flow area at the bundle centreline.

            As = (Pt - do) Ds B / Pt

        This is the one definition used by the velocity check, the heat transfer
        correlation and the pressure drop routine, so that the velocity fed to a
        correlation is the velocity that correlation assumes.

        Args:
            shell_diameter (float): Shell inside diameter [m].
            baffle_spacing (float): Baffle spacing [m].
            tube_pitch (float): Tube pitch [m].
            tube_od (float): Tube outside diameter [m].

        Returns:
            float: Cross-flow area [m2].
        """
        pitch = max(tube_pitch, 1e-9)
        return max(
            (pitch - tube_od) * max(shell_diameter, 1e-9) * max(baffle_spacing, 1e-9) / pitch,
            1e-12,
        )

    def _get_nearest_shell_id(self, shell_id_in: float, shell_ids: List[float]) -> float:
        nearest = min(shell_ids, key=lambda x: abs(x - shell_id_in))
        if abs(nearest - shell_id_in) > 1e-9:
            self._debug(f"Exact shell ID unavailable. Using nearest standard shell ID = {nearest} in")
        return nearest

    def _select_standard_tube_count(self, shell_id_m: float, tube_od_m: float, tube_passes: int) -> int | None:
        layout = self._get_standard_layout()
        od_in = round(tube_od_m / 0.0254, 2)
        shell_in = shell_id_m / 0.0254
        table = self._tube_count_tables.get(layout, {}).get(od_in)
        if not table:
            return None
        pitch_key = next(iter(table.keys()))
        shell_ids = list(table[pitch_key].keys())
        nearest_shell = self._get_nearest_shell_id(shell_in, shell_ids)
        return table[pitch_key][nearest_shell].get(tube_passes)

    def _calculate_required_area(self, q_watts: float, u_assumed: float, cltd: float) -> float:
        return self._calculate_area(q_watts, u_assumed, cltd)

    def _estimate_required_tube_count(self, area_required: float, tube_od: float, tube_length: float, tube_passes: int) -> int:
        area_per_tube = math.pi * tube_od * tube_length
        min_count = math.ceil(area_required / max(area_per_tube, 1e-12))
        return self._round_tube_count_to_passes(min_count, tube_passes)

    def _select_best_standard_geometry(self, area_required: float, tube_od: float, tube_length: float, tube_passes: int) -> Dict[str, float]:
        required_count = self._estimate_required_tube_count(area_required, tube_od, tube_length, tube_passes)
        layout = self._get_standard_layout()
        od_in = round(tube_od / 0.0254, 2)
        table = self._tube_count_tables.get(layout, {}).get(od_in, {})
        if not table:
            return {"tube_count": required_count}
        pitch_key = next(iter(table.keys()))
        candidates: List[Tuple[int, int]] = []
        for shell_id, pass_map in table[pitch_key].items():
            count = pass_map.get(tube_passes)
            if count is not None and count >= required_count:
                candidates.append((shell_id, count))
        if not candidates:
            return {"tube_count": required_count}
        candidates.sort(key=lambda x: (x[1] - required_count, x[0]))
        shell_id, count = candidates[0]
        self._debug(f"Standard geometry selected: shell ID={shell_id} in, tube_count={count}, required={required_count}")
        return {"tube_count": count, "shell_id_in": shell_id}

    def _select_next_tube_size(self, tube_od_m: float, direction: str) -> float:
        series = [0.5, 0.75, 1.0, 1.25, 1.5]
        cur = round(tube_od_m / 0.0254, 2)
        if cur not in series:
            cur = min(series, key=lambda x: abs(x-cur))
        idx = series.index(cur)
        if direction == "larger" and idx < len(series)-1:
            return series[idx+1] * 0.0254
        if direction == "smaller" and idx > 0:
            return series[idx-1] * 0.0254
        return tube_od_m

    def _get_velocity_limits(self, side: str, component) -> tuple[float, float]:
        """
        Returns recommended velocity limits based on:
        - phase
        - pressure regime
        - exchanger side
        """
    
        service = str(getattr(self, "service_type", self.specs.get("service", "heat_exchanger"))).lower()

        if service in {"condenser", "reboiler"}:
            return (0.6, 2.0) if side == "tube" else (0.3, 1.0)
        if service in {"evaporator"}:
            return (0.8, 2.0) if side == "tube" else (0.3, 1.0)

        if hasattr(component, "hx_data"):
            data = component.hx_data()
        elif isinstance(component, dict):
            data = component
        else:
            data = {}
    
        phase = str(data.get("phase", "liquid")).lower()
        family = str(data.get("family", "")).lower()
    
        pressure = (
            data.get("pressure")
            or data.get("p_bar")
            or 1.0
        )
    
        # ==========================================================
        # LIQUIDS
        # ==========================================================
    
        if phase in {"liquid"}:
    
            if side == "tube":
    
                if "water" in family:
                    return (1.5, 2.5)
    
                return (1.0, 2.5)

            return (0.5, 1.5)
    
        # ==========================================================
        # VAPORS / GASES
        # ==========================================================
    
        if pressure < 1.0:
            return (50.0, 70.0)
    
        elif pressure <= 3.0:
            return (10.0, 30.0)
    
        return (5.0, 10.0)

    def _regenerate_geometry(self, geometry: Dict[str, float], tube_passes: int, tube: Dict[str, float] | None = None) -> Dict[str, float]:
        area_per_tube = math.pi * geometry["tube_od"] * geometry["tube_length"]
        geometry["tube_count"] = self._round_tube_count_to_passes(geometry["tube_count"], tube_passes)
        geometry["area"] = geometry["tube_count"] * area_per_tube
        geometry["area_per_tube"] = area_per_tube
        geometry["tube_pitch"] = self._to_float(self.specs.get("tube_pitch"), "m") if self.specs.get("tube_pitch") is not None else (1.25 * geometry["tube_od"])
        geometry["bundle_diameter"] = self._calculate_bundle_diameter(geometry["tube_count"], geometry["tube_od"], tube_passes)
        if "shell_diameter" not in geometry:
            geometry["shell_diameter"] = self._calculate_shell_diameter(geometry["bundle_diameter"])
        area_per_tube_flow = math.pi * geometry["tube_id"] ** 2 / 4.0
        geometry["tube_flow_area"] = max(geometry["tube_count"] / max(tube_passes, 1) * area_per_tube_flow, 1e-12)
        if tube is not None:
            q_vol_tube = tube["m_dot"] / max(tube["density"], 1e-12)
            geometry["tube_velocity"] = q_vol_tube / geometry["tube_flow_area"]
        self._debug("Geometry regenerated after change")
        return geometry

    def _recalculate_required_tubes(self, base_required_area: float, geometry: Dict[str, float], tube_passes: int) -> int:
        area_per_tube = math.pi * geometry["tube_od"] * geometry["tube_length"]
        required_tubes = math.ceil(base_required_area / max(area_per_tube, 1e-12))
        required_tubes = self._round_tube_count_to_passes(required_tubes, tube_passes)
        self._debug(f"Recalculated required tubes={required_tubes} for base area={base_required_area:.4f}")
        return required_tubes

    def _get_fouling_factor(self, fluid_name: str, velocity: float | None = None, temperature_k: float | None = None) -> float:
        key = (fluid_name or "").lower()
        best = None
        for k,v in self._fouling_db.items():
            if k in key or key in k:
                best = v
                break
        if best is None:
            best = {"base": float(self.specs.get("fouling_factor", 0.0002))}
        ff = best["base"]
        if best.get("velocity_sensitive") and velocity:
            ff *= 1.15 if velocity < 1.0 else 0.9
        if best.get("temperature_sensitive") and temperature_k:
            ff *= 1.1 if temperature_k > 370 else 1.0
        return ff

    def _get_corrosion_severity(self, fluid_name: str) -> str:
        key = (fluid_name or "").lower()
        for k,v in self._corrosion_db.items():
            if k in key or key in k:
                return v
        return "medium"

    def _calculate_tube_side_score(self, props: Dict[str, float], meta: Dict[str, Any]) -> float:
        score = 0.0
        score += 5.0 if props.get("p_bar", 0) > 10 else 0.0
        score += 5.0 if meta.get("hazardous") else 0.0
        score += 4.0 if meta.get("fouling", 0.0) >= 0.0003 else 0.0
        score += 4.0 if meta.get("corrosion") in {"high", "medium-high"} else 0.0
        return score

    def _calculate_shell_side_score(self, props: Dict[str, float], meta: Dict[str, Any]) -> float:
        score = 0.0
        score += 4.0 if props.get("viscosity", 0) > 0.003 else 0.0
        score += 5.0 if meta.get("phase") in {"condensing", "boiling", "two_phase"} else 0.0
        score += 3.0 if props.get("density", 2000) < 15 else 0.0
        score += 2.0 if props.get("t_k", 0) > 500 else 0.0
        return score

    def _assign_fluids_to_sides(self, hot: Dict[str, float], cold: Dict[str, float]) -> Dict[str, Any]:
        hot_name = getattr(self.hot_in.component, "name", "hot")
        cold_name = getattr(self.cold_in.component, "name", "cold")
        hot_meta = {
            "hazardous": bool(self.specs.get("hot_hazardous", False)),
            "fouling": float(self.specs.get("hot_fouling_factor", self._get_fouling_factor(hot_name, temperature_k=hot["t_k"]))),
            "corrosion": str(self.specs.get("hot_corrosion_level", self._get_corrosion_severity(hot_name))),
            "phase": str(self.specs.get("hot_phase", hot.get("phase", "liquid"))),
        }
        cold_meta = {
            "hazardous": bool(self.specs.get("cold_hazardous", False)),
            "fouling": float(self.specs.get("cold_fouling_factor", self._get_fouling_factor(cold_name, temperature_k=cold["t_k"]))),
            "corrosion": str(self.specs.get("cold_corrosion_level", self._get_corrosion_severity(cold_name))),
            "phase": str(self.specs.get("cold_phase", cold.get("phase", "liquid"))),
        }
        hot_tube = self._calculate_tube_side_score(hot, hot_meta) - self._calculate_shell_side_score(hot, hot_meta)
        cold_tube = self._calculate_tube_side_score(cold, cold_meta) - self._calculate_shell_side_score(cold, cold_meta)
        self._debug(f"Hot fluid scoring: tube={self._calculate_tube_side_score(hot, hot_meta):.2f}, shell={self._calculate_shell_side_score(hot, hot_meta):.2f}")
        self._debug(f"Cold fluid scoring: tube={self._calculate_tube_side_score(cold, cold_meta):.2f}, shell={self._calculate_shell_side_score(cold, cold_meta):.2f}")
        if hot_tube >= cold_tube:
            scored_side = "hot"
            scored_reason = f"Hot fluid tube-side score {hot_tube:.2f} >= cold score {cold_tube:.2f}"
        else:
            scored_side = "cold"
            scored_reason = f"Cold fluid tube-side score {cold_tube:.2f} > hot score {hot_tube:.2f}"

        force_hot = bool(self.specs.get("force_hot_in_tubes"))
        force_cold = bool(self.specs.get("force_cold_in_tubes"))
        if force_hot and force_cold:
            raise ValueError(
                "force_hot_in_tubes and force_cold_in_tubes are both set; "
                "set at most one of them"
            )
        forced_side = "hot" if force_hot else "cold" if force_cold else None

        # The resolved side drives the thermal and hydraulic calculation: every
        # Kern/Bell routine takes the (tube, shell) pair from `_side_props`.
        if self._FIXED_TUBE_SIDE is not None:
            side = self._FIXED_TUBE_SIDE
            if forced_side is not None and forced_side != side:
                raise ValueError(
                    f"{type(self).__name__} models the {side} stream in the tubes; "
                    f"force_{forced_side}_in_tubes is not supported for this exchanger"
                )
            reason = [f"{type(self).__name__} models the {side} stream in the tubes", scored_reason]
            if scored_side != side:
                self._warn_with_category(
                    "ASSIGNMENT_WARNING",
                    f"Scoring recommends the {scored_side} stream in the tubes, but "
                    f"{type(self).__name__} models the {side} stream in the tubes.",
                )
        elif forced_side is not None:
            side = forced_side
            reason = [f"Forced by user: {side} in tubes", f"Scoring alone: {scored_reason}"]
        else:
            side = scored_side
            reason = [scored_reason]

        self._tube_side = side
        names = {"hot": hot_name, "cold": cold_name}
        other = {"hot": "cold", "cold": "hot"}
        self._debug(f"Fluid assignment: tube={names[side]}, shell={names[other[side]]}, reason={reason}")

        return {
            "tube_side": side,
            "tube_side_fluid": names[side],
            "shell_side_fluid": names[other[side]],
            "recommended_tube_side_fluid": names[scored_side],
            "recommended_shell_side_fluid": names[other[scored_side]],
            "assignment_reason": reason,
        }

    def _side_props(self, hot: Dict[str, float], cold: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Return the (tube, shell) stream properties for the resolved assignment."""
        return (hot, cold) if self._tube_side == "hot" else (cold, hot)

    def _hot_cold_props(self, tube: Dict[str, float], shell: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Inverse of `_side_props`: return (hot, cold) from a (tube, shell) pair."""
        return (tube, shell) if self._tube_side == "hot" else (shell, tube)

    def _side_streams(self):
        """Return the (tube, shell) inlet streams for the resolved assignment."""
        if self._tube_side == "hot":
            return self.hot_in, self.cold_in
        return self.cold_in, self.hot_in

    def _select_tube_geometry(self, area_required: float, tube: Dict[str, float], shell: Dict[str, float],
                              tube_passes: int) -> Dict[str, float]:
        tube_od = self._to_float(self.specs.get("tube_od"), "m") if self.specs.get("tube_od") is not None else None
        tube_id = self._to_float(self.specs.get("tube_id"), "m") if self.specs.get("tube_id") is not None else None
        tube_length = self._to_float(self.specs.get("tube_length"), "m") if self.specs.get("tube_length") is not None else None

        if tube_od is None or tube_id is None or tube_length is None:
            tube_stream, shell_stream = self._side_streams()
            tube_config = select_tube_configuration(
                area_required,
                {"m_dot": tube["m_dot"], "density": tube["density"], "component": tube_stream.component},
                {"m_dot": shell["m_dot"], "density": shell["density"], "component": shell_stream.component},
            )
            if tube_config:
                tube_od = tube_config["tube_od"]
                tube_id = tube_config["tube_id"]
                tube_length = tube_config["tube_length"]
                tube_count = tube_config["tube_count"]
            else:
                tube_od = 0.019
                tube_id = 0.016
                tube_length = 5.0
                tube_count = 50
        else:
            area_per_tube = math.pi * tube_od * tube_length
            self._debug("Area Per Tube: ",area_per_tube)
            tube_count = math.ceil(area_required / max(area_per_tube, 1e-12))
            self._debug("Tube Count: ",tube_count)

        # Thermo-hydraulic tube count target: satisfy area and avoid tube-side velocity collapse.
        area_per_tube = math.pi * tube_od * tube_length
        tube_flow_per_tube = math.pi * tube_id**2 / 4.0
        required_count = math.ceil(area_required / max(area_per_tube, 1e-12))
        required_count = self._round_tube_count_to_passes(required_count, tube_passes)
        vmin, vmax = self._get_velocity_limits("tube", self._side_streams()[0].component)
        q_vol_tube = tube["m_dot"] / max(tube["density"], 1e-12)
        low_v_count = int(math.floor((q_vol_tube * tube_passes) / max(vmin * tube_flow_per_tube, 1e-12)))
        high_v_count = int(math.ceil((q_vol_tube * tube_passes) / max(vmax * tube_flow_per_tube, 1e-12)))
        if high_v_count > 0:
            required_count = max(required_count, self._round_tube_count_to_passes(high_v_count, tube_passes))
        if low_v_count > 0 and required_count > low_v_count:
            self._warn_with_category("HYDRAULIC_WARNING", "Thermal area pushes tube count above hydraulic velocity target; using capped thermo-hydraulic count")
            required_count = self._round_tube_count_to_passes(low_v_count, tube_passes)

        standard_geom = self._select_best_standard_geometry(max(area_required, required_count * area_per_tube), tube_od, tube_length, tube_passes)
        std_tube_count = standard_geom.get("tube_count")
        if std_tube_count and std_tube_count >= tube_count:
            self._debug(f"Using standard tube count lookup >= required: {std_tube_count}")
            tube_count = std_tube_count
        tube_count = max(tube_count, required_count)
        tube_count_max = int(self.specs.get("tube_count_max", 1200))
        if tube_count > tube_count_max:
            self._warn_with_category("GEOMETRY_WARNING", f"Tube count clipped to practical maximum ({tube_count_max})")
            tube_count = tube_count_max
        tube_count = self._round_tube_count_to_passes(tube_count, tube_passes)
        self._debug("Tube Count Round: ",tube_count)
        tube_pitch = self._to_float(self.specs.get("tube_pitch"), "m") if self.specs.get("tube_pitch") is not None else (1.25 * tube_od)
        self._debug("Tube Pitch: ",tube_pitch)
        area = tube_count * math.pi * tube_od * tube_length
        self._debug("Tubes Surface Area: ",area)
        return {
            "tube_od": tube_od,
            "tube_id": tube_id,
            "tube_length": tube_length,
            "tube_count": tube_count,
            "tube_pitch": tube_pitch,
            "area": area,
        }

    def _calculate_bundle_diameter(
        self,
        tube_count: int,
        tube_od: float,
        tube_passes: int,
        layout: str | None = None,
    ) -> float:
        """
        Tube bundle diameter, Db = do (Nt / K1)^(1/n1).

        K1 and n1 come from `_BUNDLE_CONSTANTS` (Sinnott, Coulson & Richardson
        Vol. 6, Table 12.4) for the layout and the number of tube passes. The
        table is for a pitch of 1.25 do. A user may override the pair with the
        `bundle_k1` and `bundle_n1` specs, which must then be given together.

        Args:
            tube_count (int): Number of tubes Nt.
            tube_od (float): Tube outside diameter [m].
            tube_passes (int): Number of tube passes (1, 2, 4, 6 or 8).
            layout (str | None): "triangular" or "square"; the configured
                layout when omitted.

        Returns:
            float: Bundle diameter [m].

        Raises:
            ValueError: For a layout or pass count the table does not cover, or
                when only one of bundle_k1 / bundle_n1 is given.
        """
        k1_spec = self.specs.get("bundle_k1")
        n1_spec = self.specs.get("bundle_n1")
        if (k1_spec is None) != (n1_spec is None):
            raise ValueError("bundle_k1 and bundle_n1 must be given together")
        if k1_spec is not None:
            k1, n1 = float(k1_spec), float(n1_spec)
        else:
            layout = (layout or self._get_standard_layout()).lower()
            if layout.startswith("tri"):
                table = _BUNDLE_CONSTANTS["triangular"]
            elif layout.startswith("squ"):
                table = _BUNDLE_CONSTANTS["square"]
            else:
                raise ValueError(
                    f"No bundle diameter constants for tube layout {layout!r}; "
                    "Sinnott Table 12.4 covers 'triangular' and 'square' pitch "
                    "(give bundle_k1 and bundle_n1 to use other constants)"
                )
            passes = int(tube_passes)
            if passes not in table:
                raise ValueError(
                    f"No bundle diameter constants for {passes} tube passes; "
                    f"Sinnott Table 12.4 covers {sorted(table)} passes "
                    "(give bundle_k1 and bundle_n1 to use other constants)"
                )
            k1, n1 = table[passes]
            pitch_spec = self.specs.get("tube_pitch")
            if pitch_spec is not None:
                pitch_ratio = self._to_float(pitch_spec, "m") / max(tube_od, 1e-12)
                if abs(pitch_ratio - 1.25) > 0.0125:
                    self._warn_with_category(
                        "GEOMETRY_WARNING",
                        f"Bundle diameter uses Sinnott Table 12.4, which is for a "
                        f"pitch of 1.25 do; the pitch here is {pitch_ratio:.3f} do",
                    )
        return tube_od * math.pow(tube_count / k1, 1.0 / n1)

    def _calculate_shell_diameter(self, bundle_diameter: float) -> float:
        clearance = float(self.specs.get("bundle_clearance", max(0.02, 0.05 * bundle_diameter)))
        return bundle_diameter + clearance

    def _check_L_over_D(self, geometry: Dict[str, float], shell_diameter: float, tube_passes: int, base_required_area: float | None = None, tube: Dict[str, float] | None = None) -> Dict[str, float]:
        ld = geometry["tube_length"] / max(shell_diameter, 1e-9)
        self._debug("L/D: ",ld)
        if 5.0 <= ld <= 10.0:
            self._debug("L/D is between 5 to 10")
            return geometry
        if ld > 10.0 or ld < 5.0:
            self._debug("L/D is not between 5 to 10")
            geometry["tube_length"] = tube_length_select(geometry["tube_length"],ld)
            self._debug(f"geometry:{geometry}")
        #target_l = min(max(7.0 * shell_diameter, 0.5), 6.0)
        if self.specs.get("tube_length") is None:
            if base_required_area is not None:
                geometry["tube_count"] = self._recalculate_required_tubes(base_required_area, geometry, tube_passes)
            geometry = self._regenerate_geometry(geometry, tube_passes, tube)
            self._debug("Geometry :",geometry)
        return geometry

    def _check_velocities(
        self,
        geometry: Dict[str, float],
        tube: Dict[str, float],
        shell: Dict[str, float],
        tube_passes: int,
        shell_passes: int,
        shell_diameter: float,
    ) -> Tuple[float, float, int, float, int]:
    
        q_vol_tube = tube["m_dot"] / max(tube["density"], 1e-12)
        q_vol_shell = shell["m_dot"] / max(shell["density"], 1e-12)
        tube_stream, shell_stream = self._side_streams()
    
        area_per_tube_flow = math.pi * geometry["tube_id"]**2 / 4.0
    
        tube_flow_area = max(
            geometry["tube_count"] / max(tube_passes, 1)
            * area_per_tube_flow,
            1e-12,
        )
    
        v_tube = q_vol_tube / tube_flow_area
    
        v_min, v_max = self._get_velocity_limits(
            side="tube",
            component=tube_stream.component,
        )
    
        valid_passes = [1, 2, 4, 6, 8]
    
        for _ in range(20):
    
            if v_min <= v_tube <= v_max:
                break
    
            if v_tube < v_min:
    
                higher = [p for p in valid_passes if p > tube_passes]
    
                if not higher:
                    break
    
                tube_passes = min(higher)
    
            else:
    
                lower = [p for p in valid_passes if p < tube_passes]
    
                if not lower:
                    break
    
                tube_passes = max(lower)
    
            tube_flow_area = max(
                geometry["tube_count"] / tube_passes
                * area_per_tube_flow,
                1e-12,
            )
    
            v_tube = q_vol_tube / tube_flow_area
    
        # ==========================================================
        # SHELL SIDE
        # ==========================================================
    
        pitch = geometry["tube_pitch"]
    
        def _shell_velocity(diameter: float) -> float:
            baffle_spacing = max(0.4 * diameter, 1e-6)
            area = self._shell_crossflow_area(
                diameter, baffle_spacing, pitch, geometry["tube_od"]
            )
            return q_vol_shell / area
    
        shell_v_min, shell_v_max = self._get_velocity_limits(
            side="shell",
            component=shell_stream.component,
        )
    
        # Shrinking the shell raises the velocity, but the shell can never be
        # smaller than the bundle it has to hold.
        # With the pass count the tube side has just settled on: the bundle of
        # 8 passes is larger than the bundle of 2 for the same tube count.
        bundle_diameter = self._calculate_bundle_diameter(
            geometry["tube_count"], geometry["tube_od"], tube_passes
        )
        min_shell_diameter = self._calculate_shell_diameter(bundle_diameter)
        shell_diameter = max(shell_diameter, min_shell_diameter)

        v_shell = _shell_velocity(shell_diameter)
        settled = False
    
        for _ in range(10):
    
            if shell_v_min <= v_shell <= shell_v_max:
                settled = True
                break
    
            if v_shell < shell_v_min:
                if shell_diameter <= min_shell_diameter:
                    break
                shell_diameter = max(shell_diameter * 0.90, min_shell_diameter)
            else:
                shell_diameter *= 1.10
    
            # The returned velocity must belong to the returned shell diameter.
            v_shell = _shell_velocity(shell_diameter)
    
        if not settled:
            self._warn_with_category(
                "HYDRAULIC_WARNING",
                f"Shell velocity {v_shell:.3f} m/s is outside the "
                f"{shell_v_min}-{shell_v_max} m/s target after 10 shell diameter "
                f"adjustments; using shell diameter {shell_diameter:.4f} m",
            )
    
        return (
            v_tube,
            v_shell,
            geometry["tube_count"],
            shell_diameter,
            tube_passes,
        )


    def _validate_bundle_geometry(self, geometry: Dict[str, float]) -> tuple[bool, str]:
        tube_od = geometry.get("tube_od", 0.019)
        tube_pitch = geometry.get("tube_pitch", 1.25 * tube_od)
        shell_diameter = geometry.get("shell_diameter", 0.5)
        ligament = tube_pitch - tube_od
        if ligament < 0.15 * tube_od:
            return False, "Insufficient ligament spacing"
        packing_ratio = (geometry.get("tube_count", 1) * tube_od**2) / max(shell_diameter**2, 1e-12)
        if packing_ratio > 0.72:
            return False, "Excessive tube packing ratio"
        return True, "OK"

    def _regenerate_geometry_state(self, geometry: Dict[str, float], tube: Dict[str, float], shell: Dict[str, float], tube_passes: int, shell_passes: int) -> Dict[str, Any]:
        geometry = self._regenerate_geometry(dict(geometry), tube_passes, tube)
        v_tube, v_shell, tube_count, shell_diameter, tube_passes = self._check_velocities(
            geometry, tube, shell, tube_passes, shell_passes, geometry.get("shell_diameter", 0.5)
        )
        geometry["tube_count"] = tube_count
        geometry["shell_diameter"] = shell_diameter
        geometry = self._regenerate_geometry(geometry, tube_passes, tube)
        dimless = self._calculate_dimensionless(geometry, tube, shell, v_tube, v_shell)
        h_t, h_s = self._calculate_htc(dimless, geometry, tube, shell)
        return {
            "geometry": geometry,
            "v_tube": v_tube,
            "v_shell": v_shell,
            "tube_passes": tube_passes,
            "dimless": dimless,
            "h_t": h_t,
            "h_s": h_s,
        }

    def _calculate_dimensionless(self, geometry: Dict[str, float], tube: Dict[str, float], shell: Dict[str, float],
                                 v_tube: float, v_shell: float) -> Dict[str, float]:
        re_t = Reynolds(
            density=tube["density"],
            velocity=v_tube,
            diameter=geometry["tube_id"],
            viscosity=tube["viscosity"],
        ).calculate()
        pr_t = max(tube["cp"] * tube["viscosity"] / max(tube["k"], 1e-12), 1e-12)
        # Dittus-Boelter: the hot stream is cooled and the cold stream heated,
        # so the exponent follows the stream the assignment put in the tubes.
        n_db = _DITTUS_BOELTER_N_COOLED if self._tube_side == "hot" else _DITTUS_BOELTER_N_HEATED
        nu_t = DittusBoelter(reynolds=max(re_t, 1.0), prandtl=pr_t, n=n_db).calculate()
        self._debug(f"Tube Side Rey:{re_t}, Pra:{pr_t}, Nuss:{nu_t}")
        de_shell = self._shell_equivalent_diameter(
            geometry["tube_pitch"], geometry["tube_od"]
        )
        re_s = Reynolds(
            density=shell["density"],
            velocity=v_shell,
            diameter=de_shell,
            viscosity=shell["viscosity"],
        ).calculate()
        pr_s = max(shell["cp"] * shell["viscosity"] / max(shell["k"], 1e-12), 1e-12)
        # Kern: Nu = 0.36 Re^0.55 Pr^(1/3) (mu/mu_w)^0.14.
        phi_s = self._sieder_tate_phi("shell", shell)
        nu_s = KernShellNu(reynolds=max(re_s, 1.0), prandtl=pr_s).calculate() * phi_s
        self._debug(f"Shell Side Rey:{re_s}, Pra:{pr_s}, Nuss:{nu_s}")
        return {"re_t": re_t, "pr_t": pr_t, "nu_t": nu_t, "de_shell": de_shell, "re_s": re_s, "pr_s": pr_s, "nu_s": nu_s, "phi_s": phi_s}

    def _calculate_htc(self, dimless: Dict[str, float], geometry: Dict[str, float], tube: Dict[str, float], shell: Dict[str, float]) -> Tuple[float, float]:
        h_t = self._safe_float(ConvectiveH(nusselt=dimless["nu_t"], k=tube["k"], diameter=geometry["tube_id"]).calculate().to("W/m2K"), "h_t")
        h_s = self._safe_float(ConvectiveH(nusselt=dimless["nu_s"], k=shell["k"], diameter=dimless["de_shell"]).calculate().to("W/m2K"), "h_s")
        return h_t, h_s

    def _calculate_overall_U(
        self,
        h_t: float,
        h_s: float,
        geometry: dict,
        u_range: tuple[float, float] | None = None,
    ) -> dict:
        """
        Calculates clean and dirty overall heat transfer coefficients and resistances.
        
        Returns:
            dict: {U_clean, U_dirty, Rf_tube, Rf_shell, R_total_clean, R_total_dirty}
        """

        tube_od = geometry.get("tube_od")
        self._debug(f"Tube_od:{tube_od}")
        tube_id = geometry.get("tube_id")
        self._debug(f"Tube_id:{tube_id}")
        if tube_od is None or tube_id is None:
            raise ValueError(
                "Missing tube geometry required for "
                "overall U calculation."
            )

        # ======================================================
        # TUBE WALL RESISTANCE
        # ======================================================

        tube_od = self._safe_float(tube_od, "tube_od")
        tube_id = self._safe_float(tube_id, "tube_id")
        tube_material_k = self.specs.get(
            "tube_thermal_conductivity"
        )

        if tube_material_k is None:
            tube_material_k = 45

        # Cylindrical wall referred to the outside area, not the plane-wall form:
        #   R_wall = do ln(do/di) / (2 k)
        R_wall = (
            tube_od * math.log(max(tube_od, 1e-12) / max(tube_id, 1e-12))
            / (2.0 * tube_material_k)
        )

        # ======================================================
        # COMPONENT VALIDATION
        # ======================================================

        hot_component = getattr(self.hot_in, "component", None)
        cold_component = getattr(self.cold_in, "component", None)

        if hot_component is None:
            raise ValueError("Hot-side component not defined.")

        if cold_component is None:
            raise ValueError("Cold-side component not defined.")

        # ======================================================
        # HX METADATA
        # ======================================================

        if not hasattr(hot_component, "hx_data"):
            raise ValueError(f"{type(hot_component).__name__} does not implement hx_data().")

        if not hasattr(cold_component, "hx_data"):
            raise ValueError(f"{type(cold_component).__name__} does not implement hx_data().")

        hot_hx_data = hot_component.hx_data()
        cold_hx_data = cold_component.hx_data()

        # ======================================================
        # FOULING KEYS & PARAMETERS
        # ======================================================

        # Each fouling factor belongs to the stream the assignment put on that side.
        if self._tube_side == "hot":
            tube_hx_data, shell_hx_data = hot_hx_data, cold_hx_data
        else:
            tube_hx_data, shell_hx_data = cold_hx_data, hot_hx_data
        tube_stream, shell_stream = self._side_streams()
        tube_key = tube_hx_data.get("fouling_key")
        shell_key = shell_hx_data.get("fouling_key")

        if shell_key is None or tube_key is None:
            raise ValueError("Missing 'fouling_key' in component hx_data().")

        shell_velocity = getattr(self, "shell_velocity", None)
        tube_velocity = getattr(self, "tube_velocity", None)

        tube_temperature = self._safe_float(tube_stream.temperature.to("C"), "tube_temperature")
        shell_temperature = self._safe_float(shell_stream.temperature.to("C"), "shell_temperature")

        # ======================================================
        # FOULING FACTORS (Rf)
        # ======================================================

        Rf_shell = get_fouling_factor(
            fluid_key=shell_key,
            velocity=shell_velocity,
            temperature=shell_temperature,
            debug=True,
        )

        Rf_tube = get_fouling_factor(
            fluid_key=tube_key,
            velocity=tube_velocity,
            temperature=tube_temperature,
            debug=True,
        )

        # ======================================================
        # INDIVIDUAL CONVECTIVE RESISTANCES
        # ======================================================

        if h_t <= 0 or h_s <= 0:
            raise ValueError("Invalid heat transfer coefficients (must be > 0).")
        # Everything is referred to the tube outside area, so the tube-side film
        # and its fouling both carry the do/di ratio.
        h_t = h_t * tube_id / tube_od
        R_tube = 1 / h_t
        R_shell = 1 / h_s
        Rf_tube = Rf_tube * tube_od / max(tube_id, 1e-12)

        # ======================================================
        # TOTAL THERMAL RESISTANCES
        # ======================================================

        R_total_clean = R_tube + R_shell + R_wall
        R_total_dirty = R_tube + R_shell + R_wall + Rf_tube + Rf_shell

        if R_total_clean <= 0 or R_total_dirty <= 0:
            raise ValueError("Invalid total thermal resistance calculated.")

        # ======================================================
        # OVERALL U CALCULATION
        # ======================================================

        U_clean = 1 / R_total_clean
        U_dirty = 1 / R_total_dirty

        # ======================================================
        # DEBUGGING
        # ======================================================

        self._debug("\n" + "="*40)
        self._debug("[DEBUG] OVERALL U CALCULATION SUMMARY")
        self._debug(f"[DEBUG] Convective -> R_tube: {R_tube:.8f}, R_shell: {R_shell:.8f}")
        self._debug(f"[DEBUG] Wall       -> R_wall: {R_wall:.8f}")
        self._debug(f"[DEBUG] Fouling    -> Rf_tube: {Rf_tube:.8f}, Rf_shell: {Rf_shell:.8f}")
        self._debug("-" * 40)
        self._debug(f"[DEBUG] R_total_clean: {R_total_clean:.8f} -> U_clean: {U_clean:.4f} W/m2.K")
        self._debug(f"[DEBUG] R_total_dirty: {R_total_dirty:.8f} -> U_dirty: {U_dirty:.4f} W/m2.K")
        
        if u_range:
            u_min, u_max = u_range
            status = "WITHIN" if u_min <= U_dirty <= u_max else "OUTSIDE"
            self._debug(f"[DEBUG] Range Check: {U_dirty:.2f} is {status} limits ({u_min}, {u_max})")
        self._debug("="*40 + "\n")

        return {
            "U_clean": U_clean,
            "U_dirty": U_dirty,
            "Rf_tube": Rf_tube,
            "Rf_shell": Rf_shell,
            "R_total_clean": R_total_clean,
            "R_total_dirty": R_total_dirty,
        }

    def _validate_geometry(
        self,
        state: Dict[str, Any],
        tube_dp: float,
        shell_dp: float,
        tube: Dict[str, float],
        shell: Dict[str, float],
    ) -> Tuple[List[str], List[str]]:
    
        hard = []
        soft = []
        tube_stream, shell_stream = self._side_streams()
    
        # ==========================================================
        # AREA
        # ==========================================================
    
        if state["geometry"]["area"] < state["area_required"]:
            hard.append("area")
    
        # ==========================================================
        # TUBE VELOCITY
        # ==========================================================
    
        vmin, vmax = self._get_velocity_limits(
            side="tube",
            component=tube_stream.component,
        )
    
        vt = state["v_tube"]
    
        if vt < 0.8 * vmin or vt > 1.2 * vmax:
            hard.append("tube_velocity")
    
        elif not (vmin <= vt <= vmax):
            soft.append(
                f"Tube velocity slightly outside preferred "
                f"range ({vmin}-{vmax} m/s)"
            )
    
        # ==========================================================
        # SHELL VELOCITY
        # ==========================================================
    
        smin, smax = self._get_velocity_limits(
            side="shell",
            component=shell_stream.component,
        )
    
        vs = state["v_shell"]
    
        if vs < 0.8 * smin or vs > 1.2 * smax:
            hard.append("shell_velocity")
    
        elif not (smin <= vs <= smax):
            soft.append(
                f"Shell velocity slightly outside preferred "
                f"range ({smin}-{smax} m/s)"
            )
    
        # ==========================================================
        # PRESSURE DROP
        # ==========================================================
    
        if tube_dp > self._dp_limit(tube):
            hard.append("tube_dp")
    
        if shell_dp > self._dp_limit(shell):
            hard.append("shell_dp")
    
        # ==========================================================
        # L/D
        # ==========================================================
    
        ld = (
            state["geometry"]["tube_length"]
            / max(state["shell_diameter"], 1e-9)
        )
    
        if not (5.0 <= ld <= 10.0):
            soft.append(
                "L/D ratio outside preferred range (5-10)"
            )
    
        return hard, soft
    def _iterate_U(
        self,
        q_watts: float,
        cltd: float,
        tube: Dict[str, float],
        shell: Dict[str, float],
        shell_passes: int,
        tube_passes: int,
        u_assumed: float,
        u_range: Tuple[float, float] | None,
    ) -> Dict[str, Any]:
    
        u_user = None
        if self.specs.get("U") is not None:
            u_user = self._safe_float(self.specs["U"].to("W/m2K"), "U")
            self._trace_step("THERMAL", "U user supplied", u_user)
        state = {
            "iterations": 0,
            "u_assumed": u_assumed,
            "u_user": u_user,
            "u_history": [],
            "area_history": [],
            "geometry_history": [],
            "optimization_actions": [],
            "convergence_history": [],
            "converged": False,
        }
    
        # Relative change in U between iterations, in percent. The old test was
        # `convergence_error < 30.0` on a signed error, which accepted a 29%
        # rise and any fall at all as converged.
        tolerance_pct = float(self.specs.get("u_tolerance_percent", 1.0))
    
        # Weight of the newly calculated U in the next assumed U.
        relaxation = float(self.specs.get("u_relaxation", 0.8))
        if not 0.0 < relaxation <= 1.0:
            raise ValueError(f"u_relaxation must be in (0, 1], got {relaxation}")

        max_iter = int(self.specs.get("max_u_iterations", 15))

        # Everything one pass decides, kept so a cycle can be settled on the
        # right pass rather than whichever one the loop stopped on.
        pass_keys = (
            "area_required", "geometry", "bundle_diameter",
            "shell_diameter", "v_tube", "v_shell", "dimless", "h_t", "h_s",
            "u_calculated", "u_clean", "re_shell", "tube_dp", "shell_dp",
            "tube_passes",
        )
        passes: List[Dict[str, Any]] = []
        # A pass's hydraulic and tube-count warnings describe that pass's
        # geometry. Each pass starts again from the warnings raised before the
        # loop, so the results carry the warnings of the geometry reported and
        # not those of every geometry tried on the way to it.
        base_warnings = list(self._warnings)
        for i in range(1, max_iter + 1):
            self._warnings = list(base_warnings)
    
            self._debug(f"U Iteration = {i}")
    
            # ======================================================
            # REQUIRED AREA
            # ======================================================
    
            area_required = self._calculate_required_area(
                q_watts,
                state["u_assumed"],
                cltd,
            )
            self._trace_step("THERMAL", "U iteration", i)
            self._trace_step("THERMAL", "Area required", area_required)
    
            # ======================================================
            # GEOMETRY
            # ======================================================
    
            geometry = self._select_tube_geometry(
                area_required,
                tube,
                shell,
                tube_passes,
            )

            regen = self._regenerate_geometry_state(geometry, tube, shell, tube_passes, shell_passes)
            geometry = regen["geometry"]
            v_tube = regen["v_tube"]
            v_shell = regen["v_shell"]
            tube_passes = regen["tube_passes"]
            dimless = regen["dimless"]
            h_t, h_s = regen["h_t"], regen["h_s"]

            ok_bundle, bundle_reason = self._validate_bundle_geometry(geometry)
            if not ok_bundle:
                self._trace_step("OPTIMIZATION", "Geometry rejected", bundle_reason)
                state["optimization_actions"].append(f"reject:{bundle_reason}")
                geometry["tube_length"] = min(12.0, geometry["tube_length"] * 1.1)
                continue

            self._trace_step("GEOMETRY", "Tube count", geometry["tube_count"])
            self._trace_step("GEOMETRY", "Tube length", geometry["tube_length"])
            self._trace_step("GEOMETRY", "Shell diameter", geometry["shell_diameter"])
            self._trace_step("HYDRAULICS", "Tube velocity", v_tube)
            self._trace_step("HYDRAULICS", "Shell velocity", v_shell)
            self._trace_step("DIMENSIONLESS", "Re_tube", dimless["re_t"])
            self._trace_step("DIMENSIONLESS", "Re_shell", dimless["re_s"])
            self._trace_step("DIMENSIONLESS", "Nu_tube", dimless["nu_t"])

            bundle_diameter = self._calculate_bundle_diameter(
                geometry["tube_count"],
                geometry["tube_od"],
                tube_passes,
            )
            shell_diameter = geometry["shell_diameter"]
    
            # ======================================================
            # OVERALL U
            # ======================================================
    
            u_results = self._calculate_overall_U(
                h_t=h_t,
                h_s=h_s,
                geometry=geometry,
                u_range=u_range,
            )
    
            u_dirty = u_results["U_dirty"]
            u_clean = u_results["U_clean"]
            self._trace_step("THERMAL", "U clean", u_clean)
            self._trace_step("THERMAL", "U calculated", u_dirty)
            if u_user is not None:
                self._trace_step("THERMAL", "U calc vs U user", f"{u_dirty:.2f} vs {u_user:.2f}")
    
            # ======================================================
            # DIRTY AREA
            # ======================================================
    
            actual_area = geometry["area"]
    
            required_dirty_area = (
                q_watts
                / max(u_dirty * cltd, 1e-12)
            )
    
            # ======================================================
            # TEMPORARY STATE
            # ======================================================
    
            state.update({
                "iterations": i,
                "area_required": required_dirty_area,
                "geometry": geometry,
                "bundle_diameter": bundle_diameter,
                "shell_diameter": shell_diameter,
                "tube_passes": tube_passes,
                "v_tube": v_tube,
                "v_shell": v_shell,
                "dimless": dimless,
                "h_t": h_t,
                "h_s": h_s,
                "u_calculated": u_dirty,
                "u_clean": u_clean,
                "re_shell": dimless["re_s"],
            })
    
            # ======================================================
            # PRESSURE DROP
            # ======================================================
    
            tube_dp, shell_dp = (
                self._calculate_pressure_drop(
                    tube=tube,
                    shell=shell,
                    shell_passes=shell_passes,
                    tube_passes=tube_passes,
                    shell_diameter=shell_diameter,
                    tube_length=geometry["tube_length"],
                    tube_id=geometry["tube_id"],
                    v_tube=v_tube,
                    v_shell=v_shell,
                    geometry=geometry,
                )
            )
    
            # ======================================================
            # SAVE DP TO STATE
            # ======================================================
    
            state["tube_dp"] = tube_dp
            state["shell_dp"] = shell_dp
            self._trace_step("HYDRAULICS", "Tube pressure drop", tube_dp)
            self._trace_step("HYDRAULICS", "Shell pressure drop", shell_dp)
    
            # ======================================================
            # VALIDATION
            # ======================================================
    
            hard_violations, soft_warnings = (
                self._validate_geometry(
                    state,
                    tube_dp,
                    shell_dp,
                    tube,
                    shell,
                )
            )
    
            # ======================================================
            # U CONVERGENCE
            # ======================================================
    
            u_old = state["u_assumed"]
    
            u_new = u_dirty
    
            convergence_error = abs(
                (
                    (u_dirty - u_old)
                    / max(u_old, 1e-12)
                ) * 100.0
            )
            self._trace_step("THERMAL", "U convergence error %", convergence_error)
    
            self._debug("\n" + "=" * 60)
            self._debug(f"Iteration          : {i}")
            self._debug(f"U_assumed          : {u_old:.4f}")
            self._debug(f"U_dirty            : {u_dirty:.4f}")
            self._debug(f"U_clean            : {u_clean:.4f}")
            self._debug(f"Required Area      : {required_dirty_area:.4f} m2")
            self._debug(f"Actual Area        : {actual_area:.4f} m2")
            self._debug(f"Tube Velocity      : {v_tube:.4f} m/s")
            self._debug(f"Shell Velocity     : {v_shell:.4f} m/s")
            self._debug(f"Tube DP            : {tube_dp:.2f} Pa")
            self._debug(f"Shell DP           : {shell_dp:.2f} Pa")
            self._debug(f"U Error            : {convergence_error:.2f} %")
            self._debug("=" * 60)
    
            # ======================================================
            # UPDATE ASSUMED U
            # ======================================================
    
            # Relaxed update. When the geometry has come out the same as on the
            # previous pass, U_calc can no longer move (it is a function of the
            # geometry), so the assumed U goes straight to it and the next pass's
            # convergence test decides. Before, three identical geometries were
            # declared FAILED_CONVERGENCE while the error was still falling.
            geometry_key = (geometry["tube_count"], round(geometry["tube_length"], 3), round(shell_diameter, 3), tube_passes)
            if state["geometry_history"] and state["geometry_history"][-1] == geometry_key:
                state["u_assumed"] = u_new
            else:
                state["u_assumed"] = (1.0 - relaxation) * u_old + relaxation * u_new
            state["u_history"].append(state["u_assumed"])
            state["area_history"].append(actual_area)
            state["geometry_history"].append(geometry_key)
            passes.append({key: state[key] for key in pass_keys})
            passes[-1]["u_assumed"] = u_old
            passes[-1]["pass_warnings"] = list(self._warnings)
            passes[-1]["warnings"] = list(soft_warnings)
            state["convergence_history"].append(convergence_error)
    
            # ======================================================
            # STORE WARNINGS
            # ======================================================
    
            # This pass's soft warnings replace the previous pass's.
            state["warnings"] = list(dict.fromkeys(soft_warnings))

            # A velocity outside its band is recorded here and reported as
            # HYDRAULIC_LIMITED by `_finalize_results`. It must not skip the
            # convergence test: `_check_velocities` has already moved the tube
            # passes and shell diameter as far as they go, and the geometry is
            # reselected from the area at the top of every pass, so a tube-length
            # or shell-diameter change made here never reached the next pass.
            # Skipping the test meant a U that had settled was reported as
            # FAILED_CONVERGENCE.
            hydraulic = [v for v in hard_violations if v in ("tube_velocity", "shell_velocity")]
            if hydraulic:
                self._trace_step("OPTIMIZATION", "Hydraulic violation", hydraulic)
                state["optimization_actions"].append(f"hydraulic_violation:{hydraulic}")
    
            # ======================================================
            # CONVERGENCE CHECK
            # ======================================================
    
            # Convergence is about U alone. The hydraulic violations that call for
            # a geometry change have already sent the loop round again above, and
            # a pressure drop over its limit is a feasibility verdict, reported as
            # PRESSURE_DROP_FAILURE, not a failure of the iteration.
            if abs(convergence_error) < tolerance_pct:
    
                self._debug(
                    f"U iteration converged "
                    f"(error={convergence_error:.2f}%)"
                )
    
                state["converged"] = True
                break

            # The tube count is a step function of the assumed U, so the loop can
            # cycle between geometries that each call for the other. A geometry
            # seen before (other than on the pass just gone, handled above) means
            # it has; more passes cannot help. Settle on the smallest geometry in
            # the cycle whose area covers what its own U requires, or the largest
            # if none does.
            earlier = [j for j, key in enumerate(state["geometry_history"][:-2]) if key == geometry_key]
            if earlier:
                cycle = passes[earlier[-1]:]
                adequate = [p for p in cycle if p["geometry"]["area"] >= p["area_required"]]
                chosen = (
                    min(adequate, key=lambda p: p["geometry"]["area"])
                    if adequate
                    else max(cycle, key=lambda p: p["geometry"]["area"])
                )
                state.update({k: v for k, v in chosen.items() if k != "pass_warnings"})
                self._warnings = list(chosen["pass_warnings"])
                state["converged"] = True
                counts = sorted({p["geometry"]["tube_count"] for p in cycle})
                self._warn_with_category(
                    "CONVERGENCE_WARNING",
                    f"U cycles between tube counts {counts}; settled on "
                    f"{chosen['geometry']['tube_count']} tubes, the smallest whose "
                    f"area covers its own U" if adequate else
                    f"U cycles between tube counts {counts} and none has the area "
                    f"its own U requires; settled on the largest, "
                    f"{chosen['geometry']['tube_count']} tubes",
                )
                self._trace_step("THERMAL", "U cycle settled", chosen["geometry"]["tube_count"])
                break

        if not state.get("converged") and not state.get("status_override"):
            history = state["convergence_history"]
            if history:
                detail = f"in {len(history)} iterations; last error {history[-1]:.2f}%"
            else:
                detail = f"every one of {max_iter} geometries was rejected before U was evaluated"
            self._warn_with_category(
                "CONVERGENCE_WARNING",
                f"Overall U did not converge to {tolerance_pct}%: {detail}",
            )
            state["status_override"] = "FAILED_CONVERGENCE"
    
        return state

      
    def _calculate_pressure_drop(
        self,
        geometry: Dict[str, Any] | None,
        tube: Dict[str, float],
        shell: Dict[str, float],
        shell_velocity: float | None = None,
        tube_velocity: float | None = None,
        **kwargs: Any,
    ) -> Tuple[float, float]:
        shell_velocity = shell_velocity if shell_velocity is not None else float(kwargs.get("shell_velocity", kwargs.get("v_shell", 0.0)))
        tube_velocity = tube_velocity if tube_velocity is not None else float(kwargs.get("tube_velocity", kwargs.get("v_tube", 0.0)))
        shell_passes = int(kwargs.get("shell_passes", 1))
        tube_passes = int(kwargs.get("tube_passes", 1))
        shell_diameter = float(kwargs.get("shell_diameter", 0.0) or 0.0)
        orientation = str(kwargs.get("orientation", "horizontal")).lower()
        tube_length = float(kwargs.get("tube_length", (geometry or {}).get("tube_length", 1.0)))
        tube_id = float(kwargs.get("tube_id", (geometry or {}).get("tube_id", 0.016)))
        v_tube = tube_velocity
        v_shell = shell_velocity
    
        # ==========================================================
        # TUBE SIDE DP
        # ==========================================================
    
        re_tube = Reynolds(
            density=tube["density"],
            velocity=v_tube,
            diameter=tube_id,
            viscosity=tube["viscosity"],
        ).calculate()
    
        f_tube = self._tube_fanning_friction(re_tube, tube_id)
    
        velocity_head = tube["density"] * v_tube**2 / 2.0
        # Kern divides the straight-tube friction by phi_t = (mu/mu_w)^0.14.
        phi_t = self._sieder_tate_phi("tube", tube)
    
        # Straight-length friction plus the 4 velocity heads per pass that Kern
        # charges for the entry, exit and turns.
        tube_dp = (
            4.0
            * f_tube
            * (
                (tube_length * tube_passes)
                / max(tube_id, 1e-9)
            )
            * velocity_head
            / phi_t
        ) + (
            4.0
            * tube_passes
            * velocity_head
        )
    
        # ==========================================================
        # SHELL SIDE DP (Kern)
        # ==========================================================
    
        if geometry is None:
    
            geometry = {}
    
        tube_od = geometry.get("tube_od", 0.019)
    
        tube_pitch = geometry.get(
            "tube_pitch",
            1.25 * tube_od,
        )
    
        baffle_spacing = geometry.get(
            "baffle_spacing",
            max(0.4 * shell_diameter, 1e-6),
        )
    
        shell_dp = self._kern_shell_pressure_drop(
            shell=shell,
            v_shell=v_shell,
            shell_diameter=shell_diameter,
            baffle_spacing=baffle_spacing,
            tube_pitch=tube_pitch,
            tube_od=tube_od,
            tube_length=tube_length,
        )
    
        return tube_dp, shell_dp

    def _sieder_tate_phi(self, side: str, props: Dict[str, float]) -> float:
        """
        Sieder-Tate viscosity correction phi = (mu / mu_w)^0.14 for one side.

        mu_w is the viscosity of that side's fluid at the wall temperature. It
        is not estimated here: the component property model evaluates a
        property at the component's own temperature (25 C unless the component
        was built with another), not at a temperature the caller passes, and it
        switches phase on vapour pressure (benzene at 90 C and 1 atm comes back
        as a gas, 2.1e-5 Pa.s), so a wall viscosity taken from it would be made
        up. It is read instead from the `hot_wall_viscosity` /
        `cold_wall_viscosity` spec of the stream on that side (a Viscosity, or
        a number in Pa.s). Without one, phi = 1 is assumed and an
        ASSUMPTION_WARNING says so.

        Args:
            side (str): "tube" or "shell".
            props (Dict[str, float]): That side's stream properties.

        Returns:
            float: phi.
        """
        mu_wall = self._wall_viscosity(side)
        if mu_wall is None:
            stream = self._side_stream_name(side)
            self._warn_with_category(
                "ASSUMPTION_WARNING",
                f"Sieder-Tate (mu/mu_w)^0.14 taken as 1 on the {side} side: "
                f"no {stream}_wall_viscosity given",
            )
            return 1.0
        return (props["viscosity"] / mu_wall) ** _SIEDER_TATE_EXPONENT

    def _side_stream_name(self, side: str) -> str:
        """"hot" or "cold": the stream the assignment put on `side`."""
        if side == "tube":
            return self._tube_side
        return "cold" if self._tube_side == "hot" else "hot"

    def _wall_viscosity(self, side: str) -> float | None:
        """The wall viscosity spec of the stream on `side` [Pa.s], or None."""
        stream = self._side_stream_name(side)
        spec = self.specs.get(f"{stream}_wall_viscosity")
        if spec is None:
            return None
        mu_wall = self._to_float(spec, "Pa·s")
        if mu_wall <= 0.0:
            raise ValueError(f"{stream}_wall_viscosity must be positive, got {mu_wall} Pa.s")
        return mu_wall

    def _viscosity_correction_report(self, tube: Dict[str, float], shell: Dict[str, float]) -> Dict[str, Any]:
        """phi and its basis on each side, for the result."""
        report = {}
        for side, props in (("tube", tube), ("shell", shell)):
            mu_wall = self._wall_viscosity(side)
            report[side] = {
                "phi": self._sieder_tate_phi(side, props),
                "mu_bulk": props["viscosity"],
                "mu_wall": mu_wall,
                "basis": (
                    f"{self._side_stream_name(side)}_wall_viscosity"
                    if mu_wall is not None
                    else "assumed phi = 1 (no wall viscosity given)"
                ),
            }
        report["applied_to"] = [
            "Kern shell-side Nusselt number",
            "Kern shell-side pressure drop",
            "tube-side friction pressure drop",
        ]
        return report

    def _tube_roughness_m(self) -> float | None:
        """The `tube_roughness` spec in metres (a Length, or a number in m), or None."""
        spec = self.specs.get("tube_roughness")
        if spec is None:
            return None
        roughness = self._to_float(spec, "m")
        if roughness < 0.0:
            raise ValueError(f"tube_roughness must not be negative, got {roughness} m")
        return roughness

    def _tube_friction_model(self) -> str:
        """Name of the turbulent tube-side friction factor in use, for the report."""
        roughness = self._tube_roughness_m()
        if roughness is None:
            return "Blasius, smooth tube (no tube_roughness given)"
        return f"Colebrook-White, roughness {roughness:.3g} m"

    def _tube_fanning_friction(self, re_tube: float, tube_id: float) -> float:
        """
        Fanning friction factor for the tube side.

        The tube-side pressure drop is written with the Fanning factor,
        dP = 4 f (L Np / di) rho v^2 / 2, so every branch returns a Fanning
        factor:

        - laminar, Re < 2100: f = 16 / Re (Hagen-Poiseuille);
        - turbulent, no `tube_roughness`: Blasius smooth tube, f = 0.079 Re^-0.25;
        - turbulent with `tube_roughness`: the Colebrook-White Darcy factor of
          `processpi.calculations.fluids.ColebrookWhite`, divided by 4.

        Args:
            re_tube (float): Tube-side Reynolds number.
            tube_id (float): Tube inside diameter [m].

        Returns:
            float: Fanning friction factor.
        """
        if re_tube < _TUBE_LAMINAR_RE:
            return 16.0 / max(re_tube, 1e-9)
        roughness = self._tube_roughness_m()
        if roughness is None:
            return 0.079 / (re_tube ** 0.25)
        # ColebrookWhite takes the roughness in mm and returns the Darcy factor.
        # Its own laminar branch (Re < 2000) is never reached from here.
        darcy = self._safe_float(
            ColebrookWhite(
                reynolds_number=re_tube,
                diameter=tube_id,
                roughness=roughness * 1000.0,
            ).calculate(),
            "darcy_friction_factor",
        )
        return darcy / 4.0

    def _kern_shell_pressure_drop(
        self,
        shell: Dict[str, float],
        v_shell: float,
        shell_diameter: float,
        baffle_spacing: float,
        tube_pitch: float,
        tube_od: float,
        tube_length: float,
    ) -> float:
        """
        Kern shell-side pressure drop across the baffled bundle, nozzles excluded.

            dP_s = f G_s^2 Ds (N_b + 1) / (2 rho De phi_s)
            f    = exp(0.576 - 0.19 ln Re_s)

        with G_s = rho v_s the mass velocity on the Kern cross-flow area
        (`_shell_crossflow_area`), De the Kern equivalent diameter for the
        layout (`_shell_equivalent_diameter`), Re_s = De G_s / mu, N_b the
        number of baffles and N_b + 1 the number of bundle crossings.

        Source: D. Q. Kern, Process Heat Transfer (McGraw-Hill, 1950), the
        shell-side pressure drop and its friction factor chart (Fig. 29), in
        the SI form and curve fit given by S. Kakac, H. Liu and
        A. Pramuanjaroenkij, Heat Exchangers: Selection, Rating, and Thermal
        Design, 3rd ed. (CRC Press, 2012), Chapter 8, Kern method. f is the
        dimensionless friction factor of that form, not a Fanning or Darcy
        factor. The fit was checked here against a digitisation of Kern's chart
        (`Kern_f_Re` in the `ht` library): within 11% for 200 <= Re_s <= 1e6,
        diverging below it (Re_s = 100: 0.742 against 0.926), so a warning is
        raised outside that range.

        phi_s = (mu / mu_w)^0.14 is the Sieder-Tate viscosity correction, from
        `_sieder_tate_phi`.

        Returns:
            float: Shell-side pressure drop [Pa].
        """
        rho = shell["density"]
        de_shell = self._shell_equivalent_diameter(tube_pitch, tube_od)
        as_cross = self._shell_crossflow_area(
            shell_diameter, baffle_spacing, tube_pitch, tube_od
        )
        g_shell = rho * v_shell
        re_shell = Reynolds(
            density=rho,
            velocity=v_shell,
            diameter=de_shell,
            viscosity=shell["viscosity"],
        ).calculate()
        if re_shell <= 0.0:
            return 0.0
        if not (_KERN_SHELL_F_RE_MIN <= re_shell <= _KERN_SHELL_F_RE_MAX):
            self._warn_with_category(
                "HYDRAULIC_WARNING",
                f"Shell Re {re_shell:.0f} is outside {_KERN_SHELL_F_RE_MIN:.0f} to "
                f"{_KERN_SHELL_F_RE_MAX:.0e}, where the Kern shell-side friction "
                "factor fit was checked; the shell pressure drop is extrapolated",
            )
        f_shell = math.exp(0.576 - 0.19 * math.log(re_shell))

        # Whole baffles that fit in the tube length; the shell fluid crosses
        # the bundle once more than there are baffles.
        n_baffles = max(int(math.floor(tube_length / max(baffle_spacing, 1e-9) + 1e-9)) - 1, 0)
        phi_s = self._sieder_tate_phi("shell", shell)
        self._debug(
            f"Kern shell dP: As={as_cross:.6g} m2, G={g_shell:.6g}, Re={re_shell:.6g}, "
            f"f={f_shell:.6g}, Nb={n_baffles}"
        )
        return (
            f_shell * g_shell ** 2 * shell_diameter * (n_baffles + 1)
            / (2.0 * rho * de_shell * phi_s)
        )

    def _dp_limit(self, props: Dict[str, float]) -> float:
        mu_cp = props["viscosity"] * 1000.0
        if props["phase"] == "vapor":
            p = props["p_bar"]
            if p < 1:
                return 800.0
            if p <= 2:
                return 0.5 * p * 1e5
            return 0.1 * p * 1e5
        if mu_cp < 1:
            return 35_000.0
        if mu_cp <= 10:
            return 60_000.0
        return 70_000.0

    def _velocity_warnings(
        self,
        tube_v: float,
        shell_v: float,
        tube: Dict[str, float],
        shell: Dict[str, float],
    ) -> List[str]:
    
        warnings = []
        tube_stream, shell_stream = self._side_streams()
    
        vmin, vmax = self._get_velocity_limits(
            side="tube",
            component=tube_stream.component,
        )
    
        if tube_v > vmax:
            warnings.append(
                f"Tube velocity high "
                f"({tube_v:.2f} m/s)"
            )
    
        elif tube_v < vmin:
            warnings.append(
                f"Tube velocity low "
                f"({tube_v:.2f} m/s)"
            )
    
        smin, smax = self._get_velocity_limits(
            side="shell",
            component=shell_stream.component,
        )
    
        if shell_v > smax:
            warnings.append(
                f"Shell velocity high "
                f"({shell_v:.2f} m/s)"
            )
    
        elif shell_v < smin:
            warnings.append(
                f"Shell velocity low "
                f"({shell_v:.2f} m/s)"
            )
    
        return warnings

    def _finalize_results(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    
        """
        Finalize and normalize heat exchanger results.
        """
    
        # ==========================================================
        # WARNINGS
        # ==========================================================
    
        warnings = list(
            dict.fromkeys(
                payload.get("warnings", [])
            )
        )
    
        # ==========================================================
        # ENGINEERING FLAGS
        # ==========================================================
    
        assessment = payload.get(
            "engineering_assessment",
            "UNKNOWN",
        )
    
        if assessment in (None, "UNKNOWN"):
            # Design mode does not set one, so derive it from the checks rather
            # than reporting "UNKNOWN" for every design run.
            oversize = payload.get("oversize_ratio")
            if oversize is None:
                area_value = self._safe_float(payload.get("area", 0.0) or 0.0, "area")
                required = self._safe_float(
                    payload.get("area_required", payload.get("required_area", 0.0)) or 0.0,
                    "area_required",
                )
                oversize = area_value / required if required > 0 else None
            if oversize is not None:
                if oversize > 1.35:
                    assessment = "OVERSIZED"
                elif oversize < 1.0:
                    assessment = "UNDERSIZED"
                elif oversize < 1.05:
                    assessment = "MARGINAL"
                else:
                    assessment = "OK"
    
        thermal_ok = payload.get(
            "thermal_feasible",
            True,
        )
    
        hydraulic_ok = payload.get(
            "hydraulic_feasible",
            True,
        )
    
        pressure_ok = payload.get(
            "pressure_drop_feasible",
            True,
        )
    
        # ==========================================================
        # FINAL STATUS
        # ==========================================================
    
        # A solver that gave up outranks every downstream check: the numbers the
        # other checks are reading were never converged.
        status_override = payload.get("status_override")
    
        if status_override:
    
            status = status_override
    
        elif not thermal_ok:
    
            status = "THERMAL_FAILURE"
    
        elif not pressure_ok:
    
            status = "PRESSURE_DROP_FAILURE"
    
        elif assessment == "OVERSIZED":
    
            status = "OVERSIZED"
    
        elif not hydraulic_ok:
    
            status = "HYDRAULIC_LIMITED"
    
        elif assessment in [
    
            "OK",
            "EXCELLENT",
            "ACCEPTABLE",
    
        ]:
    
            status = "OK"
    
        elif assessment == "MARGINAL":
    
            status = "MARGINAL"
    
        else:
    
            status = assessment
    
        # ==========================================================
        # ENGINEERING INSIGHTS
        # ==========================================================
    
        engineering_insights = []
    
        # ----------------------------------------------------------
        # U VALUE
        # ----------------------------------------------------------
    
        u_calc = payload.get(
            "u_calculated",
            0.0,
        )
    
        if u_calc < 100:
    
            engineering_insights.append(
                "Very low overall heat-transfer coefficient detected. "
                "Likely caused by poor turbulence or oversized exchanger."
            )
    
        elif u_calc < 300:
    
            engineering_insights.append(
                "Moderate heat-transfer coefficient. "
                "Thermal performance may be limited."
            )
    
        else:
    
            engineering_insights.append(
                "Heat-transfer coefficient within acceptable range."
            )
    
        # ----------------------------------------------------------
        # TUBE VELOCITY
        # ----------------------------------------------------------
    
        v_tube = payload.get(
            "v_tube",
            0.0,
        )
    
        if v_tube < 0.3:
    
            engineering_insights.append(
                "Tube-side velocity extremely low. "
                "High fouling risk and poor turbulence expected."
            )
    
        elif v_tube < 1.0:
    
            engineering_insights.append(
                "Tube-side velocity acceptable but below ideal turbulent range."
            )
    
        elif v_tube > 3.0:
    
            engineering_insights.append(
                "Tube-side velocity very high. "
                "Potential erosion/vibration risk."
            )
    
        else:
    
            engineering_insights.append(
                "Tube-side velocity within recommended range."
            )
    
        # ----------------------------------------------------------
        # SHELL VELOCITY
        # ----------------------------------------------------------
    
        v_shell = payload.get(
            "v_shell",
            0.0,
        )
    
        if v_shell < 0.2:
    
            engineering_insights.append(
                "Shell-side velocity extremely low. "
                "Possible vapor blanketing and poor shell-side heat transfer."
            )
    
        elif v_shell < 0.5:
    
            engineering_insights.append(
                "Shell-side velocity slightly low."
            )
    
        elif v_shell > 2.0:
    
            engineering_insights.append(
                "Shell-side velocity very high. "
                "Potential shell-side erosion risk."
            )
    
        else:
    
            engineering_insights.append(
                "Shell-side velocity acceptable."
            )
    
        # ----------------------------------------------------------
        # PRESSURE DROP
        # ----------------------------------------------------------
    
        tube_dp = payload.get(
            "tube_dp",
            0.0,
        )
    
        shell_dp = payload.get(
            "shell_dp",
            0.0,
        )
    
        tube_dp_limit = self.specs.get(
            "tube_dp",
            Pressure(70000.0, "Pa"),
        )
    
        shell_dp_limit = self.specs.get(
            "shell_dp",
            Pressure(14000.0, "Pa"),
        )
    
        if hasattr(tube_dp_limit, "to"):
    
            tube_dp_limit = (
                tube_dp_limit
                .to("Pa")
                .value
            )
    
        if hasattr(shell_dp_limit, "to"):
    
            shell_dp_limit = (
                shell_dp_limit
                .to("Pa")
                .value
            )
    
        if tube_dp > tube_dp_limit:
    
            engineering_insights.append(
                "Tube-side pressure drop exceeds allowable limit."
            )
    
        if shell_dp > shell_dp_limit:
    
            engineering_insights.append(
                "Shell-side pressure drop exceeds allowable limit."
            )
    
        # ----------------------------------------------------------
        # OVERSIZED
        # ----------------------------------------------------------
    
        if (
    
            v_tube < 0.3
    
            and
    
            v_shell < 0.2
    
        ):
    
            engineering_insights.append(
                "Exchanger appears significantly oversized "
                "for the current operating conditions."
            )
    
        # ==========================================================
        # WARNING DETAILS
        # ==========================================================
    
        warning_details = []
    
        for w in warnings:
    
            if w.startswith("[") and "]" in w:
    
                category = (
                    w.split("]", 1)[0]
                    .replace("[", "")
                )
    
                message = (
                    w.split("]", 1)[1]
                    .strip()
                )
    
            else:
    
                category = "GENERAL_WARNING"
    
                message = w
    
            warning_details.append({
    
                "category": category,
    
                "message": message,
    
            })
    
        # ==========================================================
        # FEASIBILITY SUMMARY
        # ==========================================================
    
        feasibility_summary = {
    
            "thermal_ok": thermal_ok,
    
            "hydraulic_ok": hydraulic_ok,
    
            "pressure_drop_ok": pressure_ok,
    
            "status": status,
    
            "converged": payload.get("converged", True),
    
        }
    
        # ==========================================================
        # RETURN
        # ==========================================================
    
        return {
    
            "hx_type": "shell_and_tube",
    
            "method": payload.get(
                "method",
                self.method,
            ),
    
            "Q": HeatFlow(
                payload["q_watts_original"] / 1000.0,
                "kW",
            ),
    
            "Area": Area(
                payload["area"],
                "m2",
            ),
    
            # The area the duty needs at the reported U and corrected LMTD.
            "Area_required": (
                Area(
                    payload.get("area_required", payload.get("required_area")),
                    "m2",
                )
                if payload.get("area_required", payload.get("required_area")) is not None
                else None
            ),

            "U_assumed": HeatTransferCoefficient(
                payload["u_assumed"],
                "W/m2K",
            ),
    
            "U_user": (
    
                HeatTransferCoefficient(
                    payload.get("u_user"),
                    "W/m2K",
                )
    
                if payload.get("u_user") is not None
    
                else None
    
            ),
    
            "U_calculated": HeatTransferCoefficient(
                payload["u_calculated"],
                "W/m2K",
            ),
    
            "LMTD": payload["lmtd"],

            # The LMTD correction factor and the corrected mean temperature
            # difference F x LMTD that the area is sized or rated on.
            "ft": payload.get("ft"),

            "corrected_lmtd": payload.get("cltd"),
    
            # ======================================================
            # GEOMETRY
            # ======================================================
    
            "tube_count": payload["geometry"]["tube_count"],

            "tube_passes": payload.get("tube_passes"),

            "shell_passes": payload.get("shell_passes"),
    
            "tube_od": Length(
                payload["geometry"]["tube_od"],
                "m",
            ),
    
            "tube_id": Length(
                payload["geometry"]["tube_id"],
                "m",
            ),
    
            "tube_length": Length(
                payload["geometry"]["tube_length"],
                "m",
            ),
    
            "baffle_spacing": Length(
    
                payload["geometry"].get(
                    "baffle_spacing",
                    max(
                        0.4 * payload["shell_diameter"],
                        1e-6,
                    ),
                ),
    
                "m",
            ),
    
            "shell_diameter": Length(
                payload["shell_diameter"],
                "m",
            ),
    
            # ======================================================
            # HYDRAULICS
            # ======================================================
    
            "tube_velocity": Velocity(
                payload["v_tube"],
                "m/s",
            ),
    
            "shell_velocity": Velocity(
                payload["v_shell"],
                "m/s",
            ),
    
            "tube_dp": Pressure(
                payload["tube_dp"],
                "Pa",
            ),
    
            "shell_dp": Pressure(
                payload["shell_dp"],
                "Pa",
            ),

            # The limits the pressure drops were checked against, so a summary
            # can show them next to the actual values.
            "tube_dp_limit": (
                Pressure(payload["tube_dp_limit"], "Pa")
                if payload.get("tube_dp_limit") is not None
                else None
            ),

            "shell_dp_limit": (
                Pressure(payload["shell_dp_limit"], "Pa")
                if payload.get("shell_dp_limit") is not None
                else None
            ),

            "tube_friction_model": self._tube_friction_model(),

            "viscosity_correction": payload.get("viscosity_correction"),
    
            # ======================================================
            # THERMAL
            # ======================================================
    
            "iterations": payload.get(
                "iterations",
                1,
            ),
    
            "h_tube": payload.get("h_t"),
    
            "h_shell": payload.get("h_s"),
    
            "re_shell": payload.get("re_shell"),
    
            # ======================================================
            # STATUS
            # ======================================================
    
            "status": status,
    
            "converged": payload.get("converged", True),
    
            "warnings": warnings,
    
            "engineering_insights": engineering_insights,
    
            # ======================================================
            # ASSIGNMENT
            # ======================================================
    
            "tube_side_fluid": (
                payload.get("assignment", {})
                .get("tube_side_fluid")
            ),
    
            "shell_side_fluid": (
                payload.get("assignment", {})
                .get("shell_side_fluid")
            ),
    
            "assignment_reason": (
                payload.get("assignment", {})
                .get("assignment_reason", [])
            ),
    
            "assignment": payload.get(
                "assignment",
                {},
            ),
    
            # ======================================================
            # DEBUG
            # ======================================================
    
            "calculation_trace": list(
                self._calculation_trace
            ),
    
            "geometry_history": payload.get(
                "geometry_history",
                [],
            ),
    
            "convergence_history": payload.get(
                "convergence_history",
                [],
            ),
    
            "optimization_actions": payload.get(
                "optimization_actions",
                [],
            ),
    
            "warning_details": warning_details,
    
            "feasibility_summary": feasibility_summary,
    
            # ======================================================
            # SERVICE
            # ======================================================
    
            "service": payload.get(
                "service",
                "unknown",
            ),
    
            "phase_change": payload.get(
                "phase_change",
                False,
            ),
    
            "orientation": payload.get(
                "orientation",
                "horizontal",
            ),
    
            "condensing_side": payload.get(
                "condensing_side",
                "shell",
            ),
    
            "convergence_status": status,
    
        }

    def _design_kern(self) -> Dict[str, Any]:
        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)
        self._warnings = []
        self._validate_inputs(hot, cold)
        assignment = self._assign_fluids_to_sides(hot, cold)
        # Duty, LMTD and Ft are side-independent and stay on (hot, cold); the
        # geometry, film coefficients and hydraulics use the resolved sides.
        tube, shell = self._side_props(hot, cold)

        if hot["phase"] == "vapor":
            self.service_type = "condenser"
        elif cold["phase"] == "vapor":
            self.service_type = "vaporizer"
        elif hot["t_k"] > cold["t_k"]:
            self.service_type = "cooler"
        else:
            self.service_type = "heater"

        q_watts, th_out, tc_out = self._calculate_heat_duty(hot, cold)
        self._trace_step("THERMAL", "Heat duty (W)", q_watts)
        lmtd = self._calculate_lmtd(hot, cold, th_out, tc_out)
        self._trace_step("THERMAL", "LMTD", lmtd)

        shell_passes, tube_passes, ft = self._adjust_passes(hot, cold, th_out, tc_out)
        self._trace_step("THERMAL", "Ft", ft)
        self._trace_step("GEOMETRY", "Shell passes", shell_passes)
        self._trace_step("GEOMETRY", "Tube passes", tube_passes)
        n_units = 1
        effective_q_watts = q_watts
        if ft < 0.78:
            n_units = int(math.ceil(0.78 / max(ft, 1e-6)))
            effective_q_watts = q_watts / n_units

        cltd = max(ft * lmtd, 1e-9)
        self._debug(cltd)

        u_assumed = self._assume_u(hot, cold)
        self._trace_step("THERMAL", "U assumed initial", u_assumed)
        hot_hx = self.hot_in.component.hx_data() if hasattr(self.hot_in.component, "hx_data") else {"u_key": getattr(self.hot_in.component, "hx_type", "generic")}
        cold_hx = self.cold_in.component.hx_data() if hasattr(self.cold_in.component, "hx_data") else {"u_key": getattr(self.cold_in.component, "hx_type", "generic")}
        self._debug(f"Hot hx_data = {hot_hx}")
        self._debug(f"Cold hx_data = {cold_hx}")
        u_range = get_u_range("shell_and_tube", self.service_type, hot_hx.get("u_key", "generic"), cold_hx.get("u_key", "generic"))

        state = self._iterate_U(effective_q_watts, cltd, tube, shell, shell_passes, tube_passes, u_assumed, u_range)
        # `_check_velocities` may have moved the tube passes inside the
        # iteration; everything after it uses the passes of the settled geometry.
        tube_passes = state.get("tube_passes", tube_passes)

        # Taken after the iteration so that the hydraulic, tube-count and
        # geometry-stagnation warnings raised inside it are not lost.
        warnings: List[str] = list(getattr(self, "_warnings", []))
        warnings.extend(state.get("warnings", []))
        if n_units > 1:
            warnings.append(
                f"Using {n_units} exchangers in series to satisfy Ft requirement"
            )

        if state["shell_diameter"] > 1.5:
            warnings.append("Shell diameter too large → consider multi-shell exchanger")

        tube_dp, shell_dp = (
            self._calculate_pressure_drop(
                tube=tube,
                shell=shell,
                shell_passes=shell_passes,
                tube_passes=tube_passes,
                shell_diameter=state["shell_diameter"],
                tube_length=state["geometry"]["tube_length"],
                tube_id=state["geometry"]["tube_id"],
                v_tube=state["v_tube"],
                v_shell=state["v_shell"],
                geometry=state["geometry"],
            )
        )

        tube_limit_val = self.specs.get("tube_dp", self._dp_limit(tube))
        shell_limit_val = self.specs.get("shell_dp", self._dp_limit(shell))
        tube_limit = self._safe_float(tube_limit_val.to("Pa"), "tube_dp_limit") if hasattr(tube_limit_val, "to") else self._safe_float(tube_limit_val, "tube_dp_limit")
        shell_limit = self._safe_float(shell_limit_val.to("Pa"), "shell_dp_limit") if hasattr(shell_limit_val, "to") else self._safe_float(shell_limit_val, "shell_dp_limit")

        if tube_dp > tube_limit:
            warnings.append(f"Tube-side pressure drop {tube_dp:.1f} Pa exceeds limit {tube_limit:.1f} Pa")
        if shell_dp > shell_limit:
            warnings.append(f"Shell-side pressure drop {shell_dp:.1f} Pa exceeds limit {shell_limit:.1f} Pa")

        warnings.extend(self._velocity_warnings(state["v_tube"], state["v_shell"], tube, shell))

        if state["geometry"]["area"] < 0.85 * state["area_required"]:
            warnings.append("Area significantly undersized — redesign required")
        elif state["geometry"]["area"] < state["area_required"]:
            warnings.append("Area slightly undersized — acceptable")

        # Design mode never reported these, so `_finalize_results` had nothing to
        # build a status from and returned "UNKNOWN" for every design run.
        area_designed = state["geometry"]["area"]
        area_required = state["area_required"]
        thermal_feasible = area_designed >= area_required
        pressure_drop_feasible = tube_dp <= tube_limit and shell_dp <= shell_limit
        hydraulic_feasible = not self._velocity_warnings(
            state["v_tube"], state["v_shell"], tube, shell
        )

        payload = {
            **state,
            "warnings": list(dict.fromkeys(warnings)),
            "status_override": state.get("status_override"),
            "converged": state.get("converged", False),
            "thermal_feasible": thermal_feasible,
            "pressure_drop_feasible": pressure_drop_feasible,
            "hydraulic_feasible": hydraulic_feasible,
            "tube_dp_limit": tube_limit,
            "shell_dp_limit": shell_limit,
            "oversize_ratio": area_designed / max(area_required, 1e-12),
            "tube_side_fluid": assignment.get("tube_side_fluid"),
            "shell_side_fluid": assignment.get("shell_side_fluid"),
            "assignment_reason": assignment.get("assignment_reason", []),
            "assignment": assignment,
            "q_watts_original": q_watts,
            "q_watts_effective": effective_q_watts,
            "lmtd": lmtd,
            "cltd": cltd,
            "ft": ft,
            "n_units": n_units,
            "shell_passes": shell_passes,
            "tube_passes": tube_passes,
            "viscosity_correction": self._viscosity_correction_report(tube, shell),
            "method": "kern",
            "tube_dp": tube_dp,
            "shell_dp": shell_dp,
            "area": state["geometry"]["area"],
            "u_assumed": state["u_assumed"],
            "u_calculated": state["u_calculated"],
            "u_user": state.get("u_user"),
            "re_shell": state["re_shell"],
            "geometry_history": state.get("geometry_history", []),
            "convergence_history": state.get("convergence_history", []),
            "optimization_actions": state.get("optimization_actions", []),
        }
        return self._finalize_results(payload)

    def _calculate_ideal_shell_htc(
        self,
        kern_results: Dict[str, Any],
    ) -> float:
        """
        Ideal shell-side HTC from Kern crossflow result.
        """
    
        base_htc = float(
            kern_results.get("h_shell") or 0.0
        )
    
        return max(base_htc, 1e-9)
    
    
    def _calc_tube_row_factor(
        self,
        re_shell: float,
        ncv: float,
    ) -> float:
        """
        Bell tube row correction factor (Fn)
        """
    
        if re_shell >= 100:
            return 1.0
    
        ncv = max(ncv, 1.0)
    
        return ncv ** (-0.18)
    
    
    def _calc_window_factor(
        self,
        rw: float,
    ) -> float:
        """
        Window correction factor (Fw)
    
        rw = fraction of tubes in window zone
        """
    
        rw = max(0.0, min(rw, 0.5))
    
        fw = 1.0 - 0.72 * rw
    
        return max(0.5, min(fw, 1.0))
    
    
    def _calc_bypass_factor(
        self,
        re_shell: float,
        ab: float,
        as_cross: float,
        ns: int,
        ncv: float,
    ) -> float:
        """
        Bell bypass correction factor
        """
    
        if as_cross <= 0:
            return 1.0
    
        alpha = 1.5 if re_shell < 100 else 1.35
    
        sealing_term = (
            1.0
            - (
                (2.0 * ns)
                / max(ncv, 1.0)
            ) ** (1.0 / 3.0)
        )
    
        sealing_term = max(sealing_term, 0.0)
    
        fb = math.exp(
            -alpha
            * (ab / as_cross)
            * sealing_term
        )
    
        return max(0.5, min(fb, 1.0))
    
    
    def _calc_leakage_factor(
        self,
        atb: float,
        asb: float,
        as_cross: float,
    ) -> float:
        """
        Bell-Delaware leakage correction factor.
    
        Uses a smooth exponential approximation
        instead of overly aggressive linear penalty.
        """
    
        leakage_ratio = (
            (atb + asb)
            / max(as_cross, 1e-9)
        )
    
        fl = math.exp(
            -1.25 * leakage_ratio
        )
    
        return max(0.65, min(fl, 1.0))
        
    
    def _calc_spacing_factor(
        self,
        baffle_spacing: float,
        shell_id: float,
    ) -> float:
        """
        Baffle spacing correction factor
        """
    
        ratio = (
            baffle_spacing
            / max(shell_id, 1e-9)
        )
    
        if ratio <= 0.3:
            return 1.0
    
        if ratio >= 1.0:
            return 0.6
    
        return 1.0 - 0.57 * (ratio - 0.3)

    def _update_overall_u(self, h_tube: float, h_shell: float) -> float:
        return self.overall_u(
            h_tube=max(h_tube, 1e-9),
            h_shell=max(h_shell, 1e-9),
            fouling_factor=float(self.specs.get("fouling_factor", 0.0)),
        )

    def _design_bell_delaware(self) -> Dict[str, Any]:
    
        # ======================================================
        # START FROM KERN DESIGN
        # ======================================================
    
        kern_results = self._design_kern()
    
        data = dict(kern_results)
    
        geometry = {
            "tube_od": data["tube_od"],
            "tube_id": data["tube_id"],
            "tube_count": data["tube_count"],
            "tube_length": data["tube_length"],
            "shell_diameter": data["shell_diameter"],
            "baffle_spacing": data["baffle_spacing"],
        }
    
        # ======================================================
        # IDEAL SHELL HTC
        # ======================================================
    
        h_ideal = float(data["h_shell"])
    
        shell_id = self._safe_float(geometry["shell_diameter"], "shell_diameter")
    
        tube_od = self._safe_float(geometry["tube_od"], "tube_od")
    
        tube_pitch = tube_od * 1.25
    
        baffle_spacing = self._safe_float(geometry["baffle_spacing"], "baffle_spacing")
    
        # ======================================================
        # APPROXIMATE BELL GEOMETRY
        # ======================================================
    
        as_cross = (
            shell_id
            * baffle_spacing
            * (
                (tube_pitch - tube_od)
                / max(tube_pitch, 1e-9)
            )
        )
    
        ab = (
            0.05
            * shell_id
            * baffle_spacing
        )
    
        atb = (
            0.00025
            * math.pi
            * tube_od
            * geometry["tube_count"]
        )
        
        asb = (
            0.0015
            * shell_id
        )
    
        rw = 0.20
    
        ncv = max(
            shell_id / tube_pitch,
            1.0,
        )
    
        # ======================================================
        # ESTIMATE SHELL RE
        # ======================================================
    
        re_shell = data["re_shell"]
    
        # ======================================================
        # BELL FACTORS
        # ======================================================
    
        fn = self._calc_tube_row_factor(
            re_shell=re_shell,
            ncv=ncv,
        )
    
        fw = self._calc_window_factor(
            rw=rw,
        )
    
        fb = self._calc_bypass_factor(
            re_shell=re_shell,
            ab=ab,
            as_cross=as_cross,
            ns=0,
            ncv=ncv,
        )
    
        fl = self._calc_leakage_factor(
            atb=atb,
            asb=asb,
            as_cross=as_cross,
        )
    
        fs = self._calc_spacing_factor(
            baffle_spacing=baffle_spacing,
            shell_id=shell_id,
        )
    
        # ======================================================
        # CORRECTED SHELL HTC
        # ======================================================
    
        h_shell_corrected = (
            h_ideal
            * fn
            * fw
            * fb
            * fl
            * fs
        )
    
        # ======================================================
        # RECALCULATE OVERALL U
        # ======================================================
    
        u_results = (
            self._calculate_overall_U(
                h_t=data["h_tube"],
                h_s=h_shell_corrected,
                geometry={
                    "tube_od": tube_od,
                    "tube_id": geometry["tube_id"],
                },
            )
        )
    
        # ======================================================
        # UPDATE RESULTS
        # ======================================================
    
        data["method"] = "bell_delaware"
    
        data["h_shell_ideal"] = h_ideal
    
        data["h_shell"] = h_shell_corrected
    
        # Unit-wrapped like the Kern result this replaces; these were bare floats.
        data["U_calculated"] = HeatTransferCoefficient(
            u_results["U_dirty"],
            "W/m2K",
        )
    
        data["U_clean"] = HeatTransferCoefficient(
            u_results["U_clean"],
            "W/m2K",
        )
    
        data["bell_factors"] = {
            "Fn": fn,
            "Fw": fw,
            "Fb": fb,
            "Fl": fl,
            "Fs": fs,
        }
    
        # The shell pressure drop is the Kern one: no Bell-Delaware pressure
        # drop correlation is implemented, and the undocumented 15% uplift that
        # stood in for one is gone.
    
        return data
    def _infer_service_type(self, hot: Dict[str, float], cold: Dict[str, float]) -> str:
        explicit = str(self.specs.get("service") or getattr(self, "service_type", "")).lower()
        if explicit:
            return explicit
        if hot.get("phase") == "vapor":
            return "condenser"
        if cold.get("phase") == "vapor":
            return "reboiler"
        return "cooler" if hot["t_k"] > cold["t_k"] else "heater"

    def _calculate_service_lmtd(self, service: str, hot: Dict[str, float], cold: Dict[str, float], th_out: float, tc_out: float) -> float:
        eps = 1e-9
        service = service.lower()
        condenser_services = {"condenser", "total_condenser", "partial_condenser"}
        reboiler_services = {"reboiler", "kettle_reboiler", "thermosyphon_reboiler", "evaporator"}
        if service in condenser_services:
            t_cond = hot["t_k"]
            dt1 = t_cond - tc_out
            dt2 = t_cond - cold["t_k"]
        elif service in reboiler_services:
            t_boil = cold["t_k"]
            dt1 = hot["t_k"] - t_boil
            dt2 = th_out - t_boil
        else:
            dt1 = hot["t_k"] - tc_out
            dt2 = th_out - cold["t_k"]
        if dt1 <= 0 or dt2 <= 0:
            raise ValueError(f"Thermally infeasible terminal temperature differences for {service}: dT1={dt1:.3f} K, dT2={dt2:.3f} K")
        if abs(dt1 - dt2) <= eps:
            return 0.5 * (dt1 + dt2)
        return (dt2 - dt1) / math.log(dt2 / dt1)

    def _pressure_limit_pa(self, key: str, default_pa: float) -> float:
        raw = self.specs.get(key, Pressure(default_pa, "Pa"))
        if hasattr(raw, "to"):
            return self._safe_float(raw.to("Pa"), f"{key}_limit")
        return self._safe_float(raw, f"{key}_limit")

    def rate(self) -> Dict[str, Any]:
        self._warnings = []
        if self.hot_in is None or self.cold_in is None:
            raise ValueError("Shell-and-tube rating requires exactly one hot stream and one cold stream")
        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)
        self._validate_inputs(hot, cold)

        if self.hot_out is None or self.cold_out is None:
            raise ValueError("rate() requires hot_out and cold_out outlet stream targets")
        for stream_name, stream in (("hot_out", self.hot_out), ("cold_out", self.cold_out)):
            if getattr(stream, "temperature", None) is None:
                raise ValueError(f"rate() requires {stream_name}.temperature to be specified")

        th_out = self._safe_float(self.hot_out.temperature.to("K"), "hot_out.temperature")
        tc_out = self._safe_float(self.cold_out.temperature.to("K"), "cold_out.temperature")
        if th_out <= tc_out:
            raise ValueError("Thermally infeasible outlet targets: hot_out must be greater than cold_out for shell-and-tube rating")

        assignment = self._assign_fluids_to_sides(hot, cold)
        tube, shell = self._side_props(hot, cold)
        tube_stream, shell_stream = self._side_streams()
        service = self._infer_service_type(hot, cold)
        self.service_type = service

        condenser_services = {"condenser", "total_condenser", "partial_condenser"}
        reboiler_services = {"reboiler", "kettle_reboiler", "thermosyphon_reboiler", "evaporator"}

        if service in condenser_services:
            latent_heat = self.specs.get("latent_heat")
            if latent_heat is None:
                raise ValueError("Condenser service requires latent_heat in specs (J/kg)")
            latent_heat_jkg = self._safe_float(latent_heat.to("J/kg"), "latent_heat") if hasattr(latent_heat, "to") else self._safe_float(latent_heat, "latent_heat")
            q_actual = hot["m_dot"] * latent_heat_jkg
        elif service in reboiler_services:
            latent_heat = self.specs.get("latent_heat")
            if latent_heat is None:
                raise ValueError("Reboiler/evaporator service requires latent_heat in specs (J/kg)")
            latent_heat_jkg = self._safe_float(latent_heat.to("J/kg"), "latent_heat") if hasattr(latent_heat, "to") else self._safe_float(latent_heat, "latent_heat")
            q_actual = cold["m_dot"] * latent_heat_jkg
        else:
            q_hot = hot["m_dot"] * hot["cp"] * max(hot["t_k"] - th_out, 0.0)
            q_cold = cold["m_dot"] * cold["cp"] * max(tc_out - cold["t_k"], 0.0)
            q_actual = min(max(q_hot, 0.0), max(q_cold, 0.0))

        lmtd = self._calculate_service_lmtd(service, hot, cold, th_out, tc_out)

        # The same LMTD correction design() applies. The LMTD above is the
        # counter-current one; a shell with 2 or more tube passes is not
        # counter-current and needs F (Bowman, Mueller and Nagle 1940).
        tube_passes = int(self.specs.get("tube_passes", 2))
        shell_passes = int(self.specs.get("shell_passes", 1))
        if service in condenser_services or service in reboiler_services:
            # One stream at constant temperature: F = 1 for any pass arrangement.
            ft = 1.0
        elif shell_passes == 1 and tube_passes == 1:
            # 1-1: pure counter-current flow, which the LMTD already describes.
            ft = 1.0
        else:
            if shell_passes not in (1, 2):
                raise ValueError(
                    f"The LMTD correction factor is implemented for 1 and 2 shell "
                    f"passes, not {shell_passes}"
                )
            ft = self._calculate_ft(hot, cold, th_out, tc_out, shell_passes, tube_passes)
            if ft <= 0.0:
                raise ValueError(
                    f"Thermally infeasible outlet targets for {shell_passes} shell "
                    f"pass(es) and {tube_passes} tube passes: the LMTD correction "
                    f"factor is undefined (temperature cross)"
                )
        cltd = ft * lmtd

        user_u = self.specs.get("U")
        u_assumed = self._assume_u(hot, cold) if user_u is None else self._safe_float(user_u.to("W/m2K"), "U")
        area_spec = self.specs.get("area") or self.specs.get("Area")
        if area_spec is not None:
            area = self._safe_float(area_spec.to("m2"), "area") if hasattr(area_spec, "to") else self._safe_float(area_spec, "area")
            if area <= 0:
                raise ValueError("Provided exchanger area must be positive")
        else:
            area = q_actual / max(u_assumed * cltd, 1e-12)

        tube_od = self._safe_float(self.specs.get("tube_od", 0.01905), "tube_od")
        tube_id = self._safe_float(self.specs.get("tube_id", 0.016), "tube_id")
        tube_length = self._safe_float(self.specs.get("tube_length", 6.0), "tube_length")
        tube_pitch = self._safe_float(self.specs.get("tube_pitch", 1.25 * tube_od), "tube_pitch")
        area_per_tube = math.pi * tube_od * tube_length
        tube_count = int(self.specs.get("tube_count", max(1, math.ceil(area / max(area_per_tube, 1e-12)))))
        shell_diameter = self._safe_float(self.specs.get("shell_diameter", max(0.2, self._calculate_shell_diameter(self._calculate_bundle_diameter(tube_count, tube_od, tube_passes)))), "shell_diameter")
        baffle_spacing = self._safe_float(self.specs.get("baffle_spacing", max(0.2 * shell_diameter, 0.4 * shell_diameter)), "baffle_spacing")

        actual_area = tube_count * area_per_tube
        geometry = {"tube_count": tube_count, "tube_od": tube_od, "tube_id": tube_id, "tube_length": tube_length, "tube_pitch": tube_pitch, "shell_diameter": shell_diameter, "baffle_spacing": baffle_spacing, "area": actual_area}

        q_vol_tube = tube["m_dot"] / max(tube["density"], 1e-12)
        q_vol_shell = shell["m_dot"] / max(shell["density"], 1e-12)
        tube_flow_area = max((tube_count / max(tube_passes, 1)) * (math.pi * tube_id**2 / 4.0), 1e-12)
        shell_flow_area = self._shell_crossflow_area(shell_diameter, baffle_spacing, tube_pitch, tube_od)
        v_tube = q_vol_tube / tube_flow_area
        v_shell = q_vol_shell / shell_flow_area

        dimless = self._calculate_dimensionless(geometry, tube, shell, v_tube, v_shell)
        h_t, h_s = self._calculate_htc(dimless, geometry, tube, shell)
        u_calc = self._calculate_overall_U(h_t=h_t, h_s=h_s, geometry=geometry)["U_dirty"]

        tube_dp, shell_dp = self._calculate_pressure_drop(geometry=geometry, tube=tube, shell=shell, shell_velocity=v_shell, tube_velocity=v_tube, shell_passes=shell_passes, tube_passes=tube_passes, shell_diameter=shell_diameter, tube_length=tube_length, tube_id=tube_id)
        tube_dp_limit = self._pressure_limit_pa("tube_dp", 70000.0)
        shell_dp_limit = self._pressure_limit_pa("shell_dp", 14000.0)

        thermal_feasible = actual_area >= area
        pressure_drop_feasible = tube_dp <= tube_dp_limit and shell_dp <= shell_dp_limit
        tube_vmin, tube_vmax = self._get_velocity_limits("tube", tube_stream.component)
        shell_vmin, shell_vmax = self._get_velocity_limits("shell", shell_stream.component)
        hydraulic_feasible = tube_vmin <= v_tube <= tube_vmax and shell_vmin <= v_shell <= shell_vmax
        oversize_ratio = actual_area / max(area, 1e-12)
        if not thermal_feasible:
            assessment = "THERMAL_FAILURE"
        elif not pressure_drop_feasible:
            assessment = "PRESSURE_DROP_FAILURE"
        elif not hydraulic_feasible:
            assessment = "HYDRAULIC_LIMITED"
        elif oversize_ratio > 1.35:
            assessment = "OVERSIZED"
        elif oversize_ratio < 1.05:
            assessment = "MARGINAL"
        else:
            assessment = "OK"

        payload = {"method": self.method, "service": service, "Q": q_actual / 1000.0, "q_watts_original": q_actual, "q_watts_effective": q_actual, "lmtd": lmtd, "LMTD": lmtd, "u_assumed": u_assumed, "u_calculated": u_calc, "u_user": u_assumed if user_u is not None else None, "ft": ft, "cltd": cltd, "tube_passes": tube_passes, "shell_passes": shell_passes, "viscosity_correction": self._viscosity_correction_report(tube, shell), "area": actual_area, "required_area": area, "geometry": geometry, "tube_count": tube_count, "tube_od": tube_od, "tube_id": tube_id, "tube_length": tube_length, "tube_pitch": tube_pitch, "shell_diameter": shell_diameter, "baffle_spacing": baffle_spacing, "v_tube": v_tube, "v_shell": v_shell, "tube_velocity": v_tube, "shell_velocity": v_shell, "tube_dp": tube_dp, "shell_dp": shell_dp, "h_t": h_t, "h_s": h_s, "re_shell": dimless.get("re_s", 0.0), "engineering_assessment": assessment, "thermal_feasible": thermal_feasible, "hydraulic_feasible": hydraulic_feasible, "pressure_drop_feasible": pressure_drop_feasible, "tube_dp_limit": tube_dp_limit, "shell_dp_limit": shell_dp_limit, "warnings": list(dict.fromkeys([*self._warnings, *self._velocity_warnings(v_tube, v_shell, tube, shell)])), "assignment": assignment, "tube_side_fluid": assignment.get("tube_side_fluid"), "shell_side_fluid": assignment.get("shell_side_fluid"), "assignment_reason": assignment.get("assignment_reason", [])}

        return self._finalize_results(payload)
    def design(self) -> Dict[str, Any]:
        """
        Main design entry point for Shell & Tube HX.
        
        Supports:
        - Kern method
        - Bell-Delaware method
        
        Returns:
            Dict[str, Any]
        """
    
        # ==========================================================
        # RESET TRACE / WARNINGS
        # ==========================================================
    
        self._warnings = []
    
        if not hasattr(self, "_calculation_trace"):
            self._calculation_trace = []
    
        # ==========================================================
        # VALIDATE METHOD
        # ==========================================================
    
        if self.method not in {"kern", "bell_delaware"}:
    
            raise ValueError(
                "method must be 'kern' or 'bell_delaware'"
            )
    
        # ==========================================================
        # DEBUG HEADER
        # ==========================================================
    
        self._debug("\n" + "=" * 70)
        self._debug("STARTING SHELL & TUBE HX DESIGN")
        self._debug(f"Method : {self.method}")
        self._debug("=" * 70)
    
        # ==========================================================
        # RUN METHOD
        # ==========================================================
    
        if self.method == "kern":
    
            results = self._design_kern()
    
        elif self.method == "bell_delaware":
    
            results = self._design_bell_delaware()
    
        else:
    
            raise ValueError(
                f"Unsupported design method: {self.method}"
            )
    
        # ==========================================================
        # FINAL ENGINEERING STATUS
        # ==========================================================
    
        status = results.get("status", "UNKNOWN")
    
        self._debug("\n" + "=" * 70)
        self._debug("DESIGN COMPLETED")
        self._debug(f"Final Status : {status}")
    
        if results.get("warnings"):
    
            self._debug("\nWarnings:")
    
            for w in results["warnings"]:
    
                self._debug(f" - {w}")
    
        self._debug("=" * 70 + "\n")
    
        # ==========================================================
        # RETURN
        # ==========================================================
    
        return results
