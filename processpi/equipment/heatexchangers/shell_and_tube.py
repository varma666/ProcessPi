from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from processpi.calculations.heat_transfer.hx_kern import (
    ConvectiveH,
    DarcyDrop,
    DittusBoelter,
    KernShellNu,
    Reynolds,
)

from .base import HeatExchanger
from .standards import get_u_range, get_velocity_range, select_tube_configuration


class ShellAndTubeHX(HeatExchanger):
    def __init__(self, *args: Any, method: str = "kern", **kwargs: Any):
        self.method = method.lower()
        if self.method not in {"kern", "bell_delaware"}:
            raise ValueError("method must be 'kern' or 'bell_delaware'")
        super().__init__(*args, **kwargs)

    def _assume_u(self, hot: Dict[str, float], cold: Dict[str, float]) -> float:
        if self.specs.get("U") is not None:
            return float(self.specs["U"].to("W/m2K").value)
        hot_type = getattr(self.hot_in.component, "hx_type", "generic")
        cold_type = getattr(self.cold_in.component, "hx_type", "generic")
        service_type = getattr(self, "service_type", "heat_exchanger")
        #print(hot_type, cold_type, service_type)
        u_range = get_u_range("shell_and_tube", service_type, hot_type, cold_type)
        if u_range:
            u_min, u_max = u_range
            #print(f"Assuming overall heat transfer coefficient U = {u_min}-{u_max} W/m2K based on service and fluids")
            return 0.5 * (u_min + u_max)
        return 300.0

    def _validate_inputs(self, hot: Dict[str, float], cold: Dict[str, float]) -> None:
        required = ["cp", "density", "viscosity", "k", "m_dot", "t_k"]
        missing: List[str] = []
        for side_name, props in (("hot", hot), ("cold", cold)):
            for key in required:
                val = props.get(key)
                if val is None or val <= 0:
                    missing.append(f"{side_name}.{key}")
        if missing:
            raise ValueError(f"Missing or invalid stream properties for shell-and-tube design: {', '.join(missing)}")

    def _calculate_heat_duty(self, hot: Dict[str, float], cold: Dict[str, float]) -> Tuple[float, float, float]:
        q_kw = self.heat_duty(hot, cold)
        th_in = hot["t_k"]
        tc_in = cold["t_k"]
        print(f"Hot Cp: {hot["cp"]} Cold Cp {cold["cp"]}")
        if self.hot_out and self.hot_out.temperature:
            th_out = self.hot_out.temperature.to("K").value
        else:
            th_out = th_in - (q_kw / max(hot["m_dot"] * hot["cp"], 1e-9))

        if self.cold_out and self.cold_out.temperature:
            tc_out = self.cold_out.temperature.to("K").value
        else:
            tc_out = tc_in + (q_kw / max(cold["m_dot"] * cold["cp"], 1e-9))
            print(f"tc_out = {tc_in} + ({q_kw}/({cold["m_dot"]}*{cold["cp"]})")
            print(f"cold_rate: {max(cold["m_dot"] * cold["cp"], 1e-9)}")
        print(tc_out)
        return q_kw * 1000.0, th_out, tc_out

    def _calculate_lmtd(self, hot: Dict[str, float], cold: Dict[str, float], th_out: float, tc_out: float) -> float:
        print(f"Hot in: {hot["t_k"]} Hot out: {th_out} cold in: {cold["t_k"]} cold out: { tc_out}")
        return self.lmtd(hot["t_k"], th_out, cold["t_k"], tc_out)

    def _safe_log_ratio(self, numerator: float, denominator: float) -> float:
        if numerator <= 0.0 or denominator <= 0.0:
            raise ValueError("Log ratio arguments must be positive")
        return math.log(numerator / denominator)

    def _ft_1shell(self, r: float, s: float) -> float:
        try:
            sqrt_term = math.sqrt(r**2 + 1.0)

            numerator = sqrt_term * self._safe_log_ratio(1.0 - s, 1.0 - r * s)

            den_a = 2.0 - s * (r + 1.0 - sqrt_term)
            den_b = 2.0 - s * (r + 1.0 + sqrt_term)
            denominator = (r - 1.0) * self._safe_log_ratio(den_a, den_b)
            if abs(denominator) < 1e-12:
                return 0.0

            ft = numerator / denominator
            return max(min(ft, 1.0), 0.0)
        except Exception:
            return 0.0

    def _ft_2shell(self, r: float, s: float) -> float:
        try:
            if s <= 0.0:
                return 0.0
            sqrt_term = math.sqrt(r**2 + 1.0)

            a_term = (2.0 / s) * math.sqrt((1.0 - s) * (1.0 - r * s))
            numerator = self._safe_log_ratio(1.0 - s, 1.0 - r * s)

            den_a = a_term + sqrt_term - 1.0 - r
            den_b = a_term - sqrt_term - 1.0 - r
            denominator = self._safe_log_ratio(den_a, den_b)
            if abs(denominator) < 1e-12:
                return 0.0

            ft = numerator / denominator
            return max(min(ft, 1.0), 0.0)
        except Exception:
            return 0.0

    def _calculate_ft(self, hot: Dict[str, float], cold: Dict[str, float], th_out: float, tc_out: float,
                      shell_passes: int, tube_passes: int) -> float:
        th_in = hot["t_k"]
        tc_in = cold["t_k"]

        r = (th_in - th_out) / max(tc_out - tc_in, 1e-12)
        s = (tc_out - tc_in) / max(th_in - tc_in, 1e-12)
        print(f"R: {r} S: {s}")
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
            print(f"Passes (shell={shell_passes}, tube={tube_passes}) → Ft = {ft:.4f}")

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

    def _select_tube_geometry(self, area_required: float, hot: Dict[str, float], cold: Dict[str, float],
                              tube_passes: int) -> Dict[str, float]:
        tube_od = float(self.specs.get("tube_od")) if self.specs.get("tube_od") is not None else None
        tube_id = float(self.specs.get("tube_id")) if self.specs.get("tube_id") is not None else None
        tube_length = float(self.specs.get("tube_length")) if self.specs.get("tube_length") is not None else None

        if tube_od is None or tube_id is None or tube_length is None:
            tube_config = select_tube_configuration(
                area_required,
                {"m_dot": hot["m_dot"], "density": hot["density"], "component": self.hot_in.component},
                {"m_dot": cold["m_dot"], "density": cold["density"], "component": self.cold_in.component},
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
            tube_count = math.ceil(area_required / max(area_per_tube, 1e-12))

        tube_count = self._round_tube_count_to_passes(tube_count, tube_passes)
        tube_pitch = float(self.specs.get("tube_pitch", 1.25 * tube_od))
        area = tube_count * math.pi * tube_od * tube_length
        return {
            "tube_od": tube_od,
            "tube_id": tube_id,
            "tube_length": tube_length,
            "tube_count": tube_count,
            "tube_pitch": tube_pitch,
            "area": area,
        }

    def _calculate_bundle_diameter(self, tube_count: int) -> float:
        k1 = float(self.specs.get("bundle_k1", 0.249))
        n1 = float(self.specs.get("bundle_n1", 2.207))
        return k1 * (max(tube_count, 1) ** (1.0 / max(n1, 1e-9)))

    def _calculate_shell_diameter(self, bundle_diameter: float) -> float:
        clearance = float(self.specs.get("bundle_clearance", max(0.02, 0.05 * bundle_diameter)))
        return bundle_diameter + clearance

    def _check_L_over_D(self, geometry: Dict[str, float], shell_diameter: float, tube_passes: int) -> Dict[str, float]:
        ld = geometry["tube_length"] / max(shell_diameter, 1e-9)
        if 5.0 <= ld <= 10.0:
            return geometry

        target_l = min(max(7.0 * shell_diameter, 0.5), 6.0)
        if self.specs.get("tube_length") is None:
            geometry["tube_length"] = target_l
            area_per_tube = math.pi * geometry["tube_od"] * geometry["tube_length"]
            geometry["tube_count"] = self._round_tube_count_to_passes(
                math.ceil(geometry["area"] / max(area_per_tube, 1e-12)),
                tube_passes,
            )
            geometry["area"] = geometry["tube_count"] * area_per_tube
        return geometry

    def _check_velocities(self, geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float],
                          tube_passes: int, shell_passes: int, shell_diameter: float) -> Tuple[float, float, int, float]:
        q_vol_hot = hot["m_dot"] / max(hot["density"], 1e-12)
        q_vol_cold = cold["m_dot"] / max(cold["density"], 1e-12)

        area_per_tube_flow = math.pi * geometry["tube_id"] ** 2 / 4.0
        tube_flow = max(geometry["tube_count"] / max(tube_passes, 1) * area_per_tube_flow, 1e-12)
        v_tube = q_vol_hot / tube_flow

        v_min, v_max = get_velocity_range(self.hot_in.component)
        if v_tube > v_max:
            geometry["tube_count"] = self._round_tube_count_to_passes(int(math.ceil(geometry["tube_count"] * 1.1)), tube_passes)
            tube_flow = max(geometry["tube_count"] / max(tube_passes, 1) * area_per_tube_flow, 1e-12)
            v_tube = q_vol_hot / tube_flow
        elif v_tube < v_min:
            reduced_tubes = max(tube_passes, int(math.floor(geometry["tube_count"] * 0.85)))
            geometry["tube_count"] = self._round_tube_count_to_passes(reduced_tubes, tube_passes)
            tube_flow = max(geometry["tube_count"] / max(tube_passes, 1) * area_per_tube_flow, 1e-12)
            v_tube = q_vol_hot / tube_flow

        pitch = 1.25 * geometry["tube_od"]
        porosity = 0.6

        v_shell = 0.0
        for _ in range(5):
            baffle_spacing = max(0.4 * shell_diameter, 1e-6)
            shell_flow_area = (
                shell_diameter
                * baffle_spacing
                * porosity
                * (pitch - geometry["tube_od"]) / max(pitch, 1e-12)
            )
            v_shell = q_vol_cold / max(shell_flow_area, 1e-12)
            v_shell *= max(shell_passes, 1)

            if v_shell < 0.3:
                shell_diameter *= 0.85
            elif v_shell > 1.0:
                shell_diameter *= 1.1
            else:
                break

        return v_tube, v_shell, geometry["tube_count"], shell_diameter

    def _calculate_dimensionless(self, geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float],
                                 v_tube: float, v_shell: float) -> Dict[str, float]:
        re_t = Reynolds(
            density=hot["density"],
            velocity=v_tube,
            diameter=geometry["tube_id"],
            viscosity=hot["viscosity"],
        ).calculate()
        pr_t = max(hot["cp"] * hot["viscosity"] / max(hot["k"], 1e-12), 1e-12)
        nu_t = DittusBoelter(reynolds=max(re_t, 1.0), prandtl=pr_t, n=0.4).calculate()

        de_shell = max(1.27 * (geometry["tube_pitch"] ** 2 - 0.785 * geometry["tube_od"] ** 2) / geometry["tube_od"], 1e-6)
        re_s = Reynolds(
            density=cold["density"],
            velocity=v_shell,
            diameter=de_shell,
            viscosity=cold["viscosity"],
        ).calculate()
        pr_s = max(cold["cp"] * cold["viscosity"] / max(cold["k"], 1e-12), 1e-12)
        nu_s = KernShellNu(reynolds=max(re_s, 1.0), prandtl=pr_s).calculate()

        return {"re_t": re_t, "pr_t": pr_t, "nu_t": nu_t, "de_shell": de_shell, "re_s": re_s, "pr_s": pr_s, "nu_s": nu_s}

    def _calculate_htc(self, dimless: Dict[str, float], geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float]) -> Tuple[float, float]:
        h_t = ConvectiveH(nusselt=dimless["nu_t"], k=hot["k"], diameter=geometry["tube_id"]).calculate().to("W/m2K").value
        h_s = ConvectiveH(nusselt=dimless["nu_s"], k=cold["k"], diameter=dimless["de_shell"]).calculate().to("W/m2K").value
        return h_t, h_s

    def _calculate_overall_U(self, h_t: float, h_s: float, u_range: Tuple[float, float] | None) -> float:
        u_calculated = self.overall_u(
            h_tube=h_t,
            h_shell=h_s,
            fouling_factor=float(self.specs.get("fouling_factor", 0.0)),
        )
        u_min, u_max = u_range if u_range else (100.0, 1000.0)
        return max(min(u_calculated, u_max), u_min)

    def _iterate_U(self, q_watts: float, cltd: float, hot: Dict[str, float], cold: Dict[str, float],
                   shell_passes: int, tube_passes: int, u_assumed: float,
                   u_range: Tuple[float, float] | None) -> Dict[str, Any]:
        state: Dict[str, Any] = {"iterations": 0, "u_assumed": u_assumed}
        max_iter = 15

        for i in range(1, max_iter + 1):
            area_required = self._calculate_area(q_watts, state["u_assumed"], cltd)
            geometry = self._select_tube_geometry(area_required, hot, cold, tube_passes)

            bundle_diameter = self._calculate_bundle_diameter(geometry["tube_count"])
            shell_diameter = self._calculate_shell_diameter(bundle_diameter)

            geometry = self._check_L_over_D(geometry, shell_diameter, tube_passes)
            bundle_diameter = self._calculate_bundle_diameter(geometry["tube_count"])
            shell_diameter = self._calculate_shell_diameter(bundle_diameter)

            v_tube, v_shell, tube_count, shell_diameter = self._check_velocities(
                geometry,
                hot,
                cold,
                tube_passes,
                shell_passes,
                shell_diameter,
            )
            geometry["tube_count"] = tube_count
            geometry["area"] = geometry["tube_count"] * math.pi * geometry["tube_od"] * geometry["tube_length"]

            dimless = self._calculate_dimensionless(geometry, hot, cold, v_tube, v_shell)
            h_t, h_s = self._calculate_htc(dimless, geometry, hot, cold)
            u_calculated = self._calculate_overall_U(h_t, h_s, u_range)

            state.update(
                {
                    "iterations": i,
                    "area_required": area_required,
                    "geometry": geometry,
                    "bundle_diameter": bundle_diameter,
                    "shell_diameter": shell_diameter,
                    "v_tube": v_tube,
                    "v_shell": v_shell,
                    "dimless": dimless,
                    "h_t": h_t,
                    "h_s": h_s,
                    "u_calculated": u_calculated,
                }
            )

            if abs((u_calculated - state["u_assumed"]) / max(state["u_assumed"], 1e-9)) < 0.30:
                break
            state["u_assumed"] = u_calculated

        return state

    def _calculate_pressure_drop(self, hot: Dict[str, float], cold: Dict[str, float], shell_passes: int,
                                 tube_passes: int, shell_diameter: float, tube_length: float,
                                 tube_id: float, v_tube: float, v_shell: float) -> Tuple[float, float]:
        f_tube = float(self.specs.get("f_tube", 0.005))
        f_shell = float(self.specs.get("f_shell", 0.02))

        tube_dp = DarcyDrop(
            f=f_tube,
            length=tube_length * tube_passes,
            diameter=tube_id,
            density=hot["density"],
            velocity=v_tube,
        ).calculate().to("Pa").value

        shell_dp = DarcyDrop(
            f=f_shell,
            length=max(shell_passes, 1) * shell_diameter,
            diameter=max(shell_diameter, 1e-6),
            density=cold["density"],
            velocity=v_shell,
        ).calculate().to("Pa").value

        return tube_dp, shell_dp

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

    def _velocity_warnings(self, tube_v: float, shell_v: float, hot: Dict[str, float], cold: Dict[str, float]) -> List[str]:
        warnings: List[str] = []
        v_min, v_max = get_velocity_range(self.hot_in.component)
        if tube_v > v_max * 1.5:
            warnings.append(f"High tube velocity {tube_v:.2f} m/s → erosion risk")
        elif tube_v > v_max:
            warnings.append(f"Tube velocity slightly high ({v_min}-{v_max} m/s recommended)")
        elif tube_v < v_min * 0.5:
            warnings.append(f"Low tube velocity {tube_v:.2f} m/s → fouling risk")
        elif tube_v < v_min:
            warnings.append(f"Tube velocity slightly low ({v_min}-{v_max} m/s recommended)")

        if cold["phase"] == "vapor":
            p = cold["p_bar"]
            target = (50, 70) if p < 1 else ((10, 30) if p <= 2 else (5, 10))
        else:
            target = (0.3, 1.0)
        if not (target[0] <= shell_v <= target[1]):
            warnings.append(f"Shell velocity {shell_v:.2f} m/s outside recommended {target[0]}-{target[1]} m/s")
        return warnings

    def _finalize_results(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        warnings = list(dict.fromkeys(payload["warnings"]))
        critical: List[str] = []
        advisory: List[str] = []
        for w in warnings:
            wl = w.lower()
            if "pressure drop" in wl or "significantly undersized" in wl or "erosion risk" in wl:
                critical.append(w)
            else:
                advisory.append(w)

        if critical:
            status = "VIOLATION"
        elif advisory:
            status = "WARNING"
        else:
            status = "OK"

        return {
            "hx_type": "shell_and_tube",
            "method": payload.get("method", self.method),
            "Q": payload["q_watts_original"] / 1000.0,
            "Area": payload["area"],
            "U_assumed": payload["u_assumed"],
            "U_calculated": payload["u_calculated"],
            "LMTD": payload["lmtd"],
            "tube_count": payload["geometry"]["tube_count"],
            "tube_od": payload["geometry"]["tube_od"],
            "tube_id": payload["geometry"]["tube_id"],
            "baffle_spacing": max(0.4 * payload["shell_diameter"], 1e-6),
            "shell_diameter": payload["shell_diameter"],
            "tube_velocity": payload["v_tube"],
            "shell_velocity": payload["v_shell"],
            "tube_dp": payload["tube_dp"],
            "shell_dp": payload["shell_dp"],
            "iterations": payload["iterations"],
            "h_tube": payload.get("h_t"),
            "h_shell": payload.get("h_s"),
            "status": status,
            "warnings": warnings,
        }

    def _design_kern(self) -> Dict[str, Any]:
        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)
        self._warnings = []
        self._validate_inputs(hot, cold)

        if hot["phase"] == "vapor":
            self.service_type = "condenser"
        elif cold["phase"] == "vapor":
            self.service_type = "vaporizer"
        elif hot["t_k"] > cold["t_k"]:
            self.service_type = "cooler"
        else:
            self.service_type = "heater"

        q_watts, th_out, tc_out = self._calculate_heat_duty(hot, cold)
        print(q_watts)
        lmtd = self._calculate_lmtd(hot, cold, th_out, tc_out)
        print(lmtd)

        shell_passes, tube_passes, ft = self._adjust_passes(hot, cold, th_out, tc_out)
        print(ft, shell_passes, tube_passes)
        warnings: List[str] = list(getattr(self, "_warnings", []))

        n_units = 1
        effective_q_watts = q_watts
        if ft < 0.78:
            n_units = int(math.ceil(0.78 / max(ft, 1e-6)))
            effective_q_watts = q_watts / n_units
            warnings.append(f"Using {n_units} exchangers in series to satisfy Ft requirement")

        cltd = max(ft * lmtd, 1e-9)
        print(cltd)

        u_assumed = self._assume_u(hot, cold)
        print(u_assumed)
        hot_type = getattr(self.hot_in.component, "hx_type", "generic")
        cold_type = getattr(self.cold_in.component, "hx_type", "generic")
        u_range = get_u_range("shell_and_tube", self.service_type, hot_type, cold_type)

        state = self._iterate_U(effective_q_watts, cltd, hot, cold, shell_passes, tube_passes, u_assumed, u_range)

        if state["shell_diameter"] > 1.5:
            warnings.append("Shell diameter too large → consider multi-shell exchanger")

        tube_dp, shell_dp = self._calculate_pressure_drop(
            hot=hot,
            cold=cold,
            shell_passes=shell_passes,
            tube_passes=tube_passes,
            shell_diameter=state["shell_diameter"],
            tube_length=state["geometry"]["tube_length"],
            tube_id=state["geometry"]["tube_id"],
            v_tube=state["v_tube"],
            v_shell=state["v_shell"],
        )

        tube_limit_val = self.specs.get("tube_dp", self._dp_limit(hot))
        shell_limit_val = self.specs.get("shell_dp", self._dp_limit(cold))
        tube_limit = float(tube_limit_val.to("Pa").value) if hasattr(tube_limit_val, "to") else float(tube_limit_val)
        shell_limit = float(shell_limit_val.to("Pa").value) if hasattr(shell_limit_val, "to") else float(shell_limit_val)

        if tube_dp > tube_limit:
            warnings.append(f"Tube-side pressure drop {tube_dp:.1f} Pa exceeds limit {tube_limit:.1f} Pa")
        if shell_dp > shell_limit:
            warnings.append(f"Shell-side pressure drop {shell_dp:.1f} Pa exceeds limit {shell_limit:.1f} Pa")

        warnings.extend(self._velocity_warnings(state["v_tube"], state["v_shell"], hot, cold))

        if state["geometry"]["area"] < 0.85 * state["area_required"]:
            warnings.append("Area significantly undersized — redesign required")
        elif state["geometry"]["area"] < state["area_required"]:
            warnings.append("Area slightly undersized — acceptable")

        payload = {
            **state,
            "warnings": warnings,
            "q_watts_original": q_watts,
            "q_watts_effective": effective_q_watts,
            "lmtd": lmtd,
            "cltd": cltd,
            "ft": ft,
            "n_units": n_units,
            "method": "kern",
            "tube_dp": tube_dp,
            "shell_dp": shell_dp,
            "area": state["geometry"]["area"],
            "u_assumed": state["u_assumed"],
            "u_calculated": state["u_calculated"],
        }
        return self._finalize_results(payload)

    def _calculate_ideal_shell_htc(self, kern_results: Dict[str, Any]) -> float:
        base_htc = float(kern_results.get("h_shell") or 0.0)
        return max(base_htc, 1e-9)

    def _calc_baffle_cut_factor(self) -> float:
        return 0.8

    def _calc_leakage_factor(self) -> float:
        return 0.7

    def _calc_bypass_factor(self) -> float:
        return 0.75

    def _calc_laminar_factor(self) -> float:
        return 1.0

    def _calc_spacing_factor(self) -> float:
        return 0.9

    def _update_overall_u(self, h_tube: float, h_shell: float) -> float:
        return self.overall_u(
            h_tube=max(h_tube, 1e-9),
            h_shell=max(h_shell, 1e-9),
            fouling_factor=float(self.specs.get("fouling_factor", 0.0)),
        )

    def _design_bell_delaware(self) -> Dict[str, Any]:
        results = self._design_kern()
        h_ideal = self._calculate_ideal_shell_htc(results)

        j_c = self._calc_baffle_cut_factor()
        j_l = self._calc_leakage_factor()
        j_b = self._calc_bypass_factor()
        j_r = self._calc_laminar_factor()
        j_s = self._calc_spacing_factor()

        h_shell = h_ideal * j_c * j_l * j_b * j_r * j_s
        h_tube = float(results.get("h_tube") or 0.0)
        u_new = self._update_overall_u(h_tube, h_shell)

        updated = dict(results)
        updated["h_shell_ideal"] = h_ideal
        updated["h_shell"] = h_shell
        updated["U_calculated"] = u_new
        updated["method"] = "bell_delaware"
        return updated

    def design(self) -> Dict[str, Any]:
        if self.method == "kern":
            return self._design_kern()
        if self.method == "bell_delaware":
            return self._design_bell_delaware()
        raise ValueError("method must be 'kern' or 'bell_delaware'")
