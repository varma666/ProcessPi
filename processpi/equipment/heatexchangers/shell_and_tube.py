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


class ShellAndTubeHX(HeatExchanger):
    def __init__(self, *args: Any, method: str = "kern", **kwargs: Any):
        self.method = method.lower()
        if self.method not in {"kern", "bell_delaware"}:
            raise ValueError("method must be 'kern' or 'bell_delaware'")
        super().__init__(*args, **kwargs)
        self._load_standard_tables()

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
                print(f"Side name {side_name}, {key} : {val}")
                if val is None or val <= 0:
                    
                    missing.append(f"{side_name}.{key}")
        if missing:
            raise ValueError(f"Missing or invalid stream properties for shell-and-tube design: {', '.join(missing)}")

    def _calculate_heat_duty(self, hot: Dict[str, float], cold: Dict[str, float]) -> Tuple[float, float, float]:
        q_kw = self.heat_duty(hot, cold)
        th_in = hot["t_k"]
        tc_in = cold["t_k"]
        print(f"Hot Cp: {hot["cp"]} Cold Cp {cold["cp"]}")
        if self.hot_out and self.hot_out.temperature and self.hot_out.temperature.to("C").value == 25 :
            th_out = self.hot_out.temperature.to("K").value
        else:
            th_out = th_in - (q_kw / max(hot["m_dot"] * hot["cp"], 1e-9))

        if self.cold_out and self.cold_out.temperature and self.cold_out.temperature.to("C").value == 25:
            print("Hello World")
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

    def _debug(self, message: str) -> None:
        print(f"[DEBUG] {message}")

    def _load_standard_tables(self) -> None:
        self._tube_count_tables = STANDARD_TUBE_COUNT_TABLES
        self._fouling_db = FOULING_FACTOR_DATABASE
        self._corrosion_db = CORROSION_SEVERITY_DATABASE

    def _get_standard_layout(self) -> str:
        return str(self.specs.get("tube_layout", "triangular")).lower()

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
    
                return (1.0, 2.0)
    
            return (0.3, 1.0)
    
        # ==========================================================
        # VAPORS / GASES
        # ==========================================================
    
        if pressure < 1.0:
            return (50.0, 70.0)
    
        elif pressure <= 3.0:
            return (10.0, 30.0)
    
        return (5.0, 10.0)

    def _regenerate_geometry(self, geometry: Dict[str, float], tube_passes: int, hot: Dict[str, float] | None = None) -> Dict[str, float]:
        area_per_tube = math.pi * geometry["tube_od"] * geometry["tube_length"]
        geometry["tube_count"] = self._round_tube_count_to_passes(geometry["tube_count"], tube_passes)
        geometry["area"] = geometry["tube_count"] * area_per_tube
        geometry["area_per_tube"] = area_per_tube
        geometry["tube_pitch"] = float(self.specs.get("tube_pitch", 1.25 * geometry["tube_od"]))
        geometry["bundle_diameter"] = self._calculate_bundle_diameter(geometry["tube_count"], geometry["tube_od"])
        geometry["shell_diameter"] = self._calculate_shell_diameter(geometry["bundle_diameter"])
        area_per_tube_flow = math.pi * geometry["tube_id"] ** 2 / 4.0
        geometry["tube_flow_area"] = max(geometry["tube_count"] / max(tube_passes, 1) * area_per_tube_flow, 1e-12)
        if hot is not None:
            q_vol_hot = hot["m_dot"] / max(hot["density"], 1e-12)
            geometry["tube_velocity"] = q_vol_hot / geometry["tube_flow_area"]
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
        if self.specs.get("force_hot_in_tubes"):
            tube, shell = hot_name, cold_name
            reason=["Forced by user: hot in tubes"]
        elif self.specs.get("force_cold_in_tubes"):
            tube, shell = cold_name, hot_name
            reason=["Forced by user: cold in tubes"]
        elif hot_tube >= cold_tube:
            tube, shell = hot_name, cold_name
            reason=[f"Hot fluid tube-side score {hot_tube:.2f} >= cold score {cold_tube:.2f}"]
        else:
            tube, shell = cold_name, hot_name
            reason=[f"Cold fluid tube-side score {cold_tube:.2f} > hot score {hot_tube:.2f}"]
        self._debug(f"Fluid assignment: tube={tube}, shell={shell}, reason={reason}")
        return {"tube_side_fluid": tube, "shell_side_fluid": shell, "assignment_reason": reason}

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
            print("Area Per Tube: ",area_per_tube)
            tube_count = math.ceil(area_required / max(area_per_tube, 1e-12))
            print("Tube Count: ",tube_count)

        standard_geom = self._select_best_standard_geometry(area_required, tube_od, tube_length, tube_passes)
        std_tube_count = standard_geom.get("tube_count")
        if std_tube_count and std_tube_count >= tube_count:
            self._debug(f"Using standard tube count lookup >= required: {std_tube_count}")
            tube_count = std_tube_count
        tube_count = self._round_tube_count_to_passes(tube_count, tube_passes)
        print("Tube Count Round: ",tube_count)
        tube_pitch = float(self.specs.get("tube_pitch", 1.25 * tube_od))
        print("Tube Pitch: ",tube_pitch)
        area = tube_count * math.pi * tube_od * tube_length
        print("Tubes Surface Area: ",area)
        return {
            "tube_od": tube_od,
            "tube_id": tube_id,
            "tube_length": tube_length,
            "tube_count": tube_count,
            "tube_pitch": tube_pitch,
            "area": area,
        }

    def _calculate_bundle_diameter(self, tube_count: int , tube_od: float) -> float:
        k1 = float(self.specs.get("bundle_k1", 0.249))
        n1 = float(self.specs.get("bundle_n1", 2.207))
        Db = tube_od * math.pow((tube_count/k1),(1/n1))
        return Db

    def _calculate_shell_diameter(self, bundle_diameter: float) -> float:
        clearance = float(self.specs.get("bundle_clearance", max(0.02, 0.05 * bundle_diameter)))
        return bundle_diameter + clearance

    def _check_L_over_D(self, geometry: Dict[str, float], shell_diameter: float, tube_passes: int, base_required_area: float | None = None, hot: Dict[str, float] | None = None) -> Dict[str, float]:
        ld = geometry["tube_length"] / max(shell_diameter, 1e-9)
        print("L/D: ",ld)
        if 5.0 <= ld <= 10.0:
            print("L/D is between 5 to 10")
            return geometry
        if ld > 10.0 or ld < 5.0:
            print("L/D is not between 5 to 10")
            geometry["tube_length"] = tube_length_select(geometry["tube_length"],ld)
            print(f"geometry:{geometry}")
        #target_l = min(max(7.0 * shell_diameter, 0.5), 6.0)
        if self.specs.get("tube_length") is None:
            if base_required_area is not None:
                geometry["tube_count"] = self._recalculate_required_tubes(base_required_area, geometry, tube_passes)
            geometry = self._regenerate_geometry(geometry, tube_passes, hot)
            print("Geometry :",geometry)
        return geometry

    def _check_velocities(
        self,
        geometry: Dict[str, float],
        hot: Dict[str, float],
        cold: Dict[str, float],
        tube_passes: int,
        shell_passes: int,
        shell_diameter: float,
    ) -> Tuple[float, float, int, float, int]:
    
        q_vol_hot = hot["m_dot"] / max(hot["density"], 1e-12)
        q_vol_cold = cold["m_dot"] / max(cold["density"], 1e-12)
    
        area_per_tube_flow = math.pi * geometry["tube_id"]**2 / 4.0
    
        tube_flow_area = max(
            geometry["tube_count"] / max(tube_passes, 1)
            * area_per_tube_flow,
            1e-12,
        )
    
        v_tube = q_vol_hot / tube_flow_area
    
        v_min, v_max = self._get_velocity_limits(
            side="tube",
            component=self.hot_in.component,
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
    
            v_tube = q_vol_hot / tube_flow_area
    
        # ==========================================================
        # SHELL SIDE
        # ==========================================================
    
        pitch = geometry["tube_pitch"]
    
        porosity = 0.6
    
        for _ in range(10):
    
            baffle_spacing = max(
                0.4 * shell_diameter,
                1e-6,
            )
    
            shell_flow_area = (
                shell_diameter
                * baffle_spacing
                * porosity
                * (pitch - geometry["tube_od"])
                / max(pitch, 1e-12)
            )
    
            v_shell = (
                q_vol_cold
                / max(shell_flow_area, 1e-12)
            )
    
            shell_v_min, shell_v_max = self._get_velocity_limits(
                side="shell",
                component=self.cold_in.component,
            )
    
            if shell_v_min <= v_shell <= shell_v_max:
                break
    
            if v_shell < shell_v_min:
                shell_diameter *= 0.90
            else:
                shell_diameter *= 1.10
    
        return (
            v_tube,
            v_shell,
            geometry["tube_count"],
            shell_diameter,
            tube_passes,
        )

    def _calculate_dimensionless(self, geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float],
                                 v_tube: float, v_shell: float) -> Dict[str, float]:
        re_t = Reynolds(
            density=hot["density"],
            velocity=v_tube,
            diameter=geometry["tube_id"],
            viscosity=hot["viscosity"],
        ).calculate()
        pr_t = max(hot["cp"] * 1000 * hot["viscosity"] / max(hot["k"], 1e-12), 1e-12)
        nu_t = DittusBoelter(reynolds=max(re_t, 1.0), prandtl=pr_t, n=0.4).calculate()
        print(f"Tube Side Rey:{re_t}, Pra:{pr_t}, Nuss:{nu_t}")
        de_shell = max(1.27 * (geometry["tube_pitch"] ** 2 - 0.785 * geometry["tube_od"] ** 2) / geometry["tube_od"], 1e-6)
        re_s = Reynolds(
            density=cold["density"],
            velocity=v_shell,
            diameter=de_shell,
            viscosity=cold["viscosity"],
        ).calculate()
        pr_s = max(cold["cp"] * 1000 * cold["viscosity"] / max(cold["k"], 1e-12), 1e-12)
        nu_s = KernShellNu(reynolds=max(re_s, 1.0), prandtl=pr_s).calculate()
        print(f"Shell Side Rey:{re_s}, Pra:{pr_s}, Nuss:{nu_s}")
        return {"re_t": re_t, "pr_t": pr_t, "nu_t": nu_t, "de_shell": de_shell, "re_s": re_s, "pr_s": pr_s, "nu_s": nu_s}

    def _calculate_htc(self, dimless: Dict[str, float], geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float]) -> Tuple[float, float]:
        h_t = ConvectiveH(nusselt=dimless["nu_t"], k=hot["k"], diameter=geometry["tube_id"]).calculate().to("W/m2K").value
        h_s = ConvectiveH(nusselt=dimless["nu_s"], k=cold["k"], diameter=dimless["de_shell"]).calculate().to("W/m2K").value
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
        print(f"Tube_od:{tube_od}")
        tube_id = geometry.get("tube_id")
        print(f"Tube_id:{tube_id}")
        if tube_od is None or tube_id is None:
            raise ValueError(
                "Missing tube geometry required for "
                "overall U calculation."
            )

        # ======================================================
        # TUBE WALL RESISTANCE
        # ======================================================

        tube_wall_thickness = (tube_od - tube_id) / 2

        tube_material_k = self.specs.get(
            "tube_thermal_conductivity"
        )

        if tube_material_k is None:
            tube_material_k = 45
        
        R_wall = tube_wall_thickness / tube_material_k

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

        shell_key = hot_hx_data.get("fouling_key")
        tube_key = cold_hx_data.get("fouling_key")

        if shell_key is None or tube_key is None:
            raise ValueError("Missing 'fouling_key' in component hx_data().")

        shell_velocity = getattr(self, "shell_velocity", None)
        tube_velocity = getattr(self, "tube_velocity", None)

        shell_temperature = self.hot_in.temperature.to("C").value
        tube_temperature = self.cold_in.temperature.to("C").value

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

        R_tube = 1 / h_t
        R_shell = 1 / h_s

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

        print("\n" + "="*40)
        print("[DEBUG] OVERALL U CALCULATION SUMMARY")
        print(f"[DEBUG] Convective -> R_tube: {R_tube:.8f}, R_shell: {R_shell:.8f}")
        print(f"[DEBUG] Wall       -> R_wall: {R_wall:.8f}")
        print(f"[DEBUG] Fouling    -> Rf_tube: {Rf_tube:.8f}, Rf_shell: {Rf_shell:.8f}")
        print("-" * 40)
        print(f"[DEBUG] R_total_clean: {R_total_clean:.8f} -> U_clean: {U_clean:.4f} W/m2.K")
        print(f"[DEBUG] R_total_dirty: {R_total_dirty:.8f} -> U_dirty: {U_dirty:.4f} W/m2.K")
        
        if u_range:
            u_min, u_max = u_range
            status = "WITHIN" if u_min <= U_dirty <= u_max else "OUTSIDE"
            print(f"[DEBUG] Range Check: {U_dirty:.2f} is {status} limits ({u_min}, {u_max})")
        print("="*40 + "\n")

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
        hot: Dict[str, float],
        cold: Dict[str, float],
    ) -> Tuple[List[str], List[str]]:
    
        hard = []
        soft = []
    
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
            component=self.hot_in.component,
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
            component=self.cold_in.component,
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
    
        if tube_dp > self._dp_limit(hot):
            hard.append("tube_dp")
    
        if shell_dp > self._dp_limit(cold):
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
        hot: Dict[str, float],
        cold: Dict[str, float],
        shell_passes: int,
        tube_passes: int,
        u_assumed: float,
        u_range: Tuple[float, float] | None,
    ) -> Dict[str, Any]:
    
        state = {
            "iterations": 0,
            "u_assumed": u_assumed,
        }
    
        max_iter = 15
    
        for i in range(1, max_iter + 1):
    
            self._debug(f"U Iteration = {i}")
    
            # ======================================================
            # REQUIRED AREA
            # ======================================================
    
            area_required = self._calculate_required_area(
                q_watts,
                state["u_assumed"],
                cltd,
            )
    
            # ======================================================
            # GEOMETRY
            # ======================================================
    
            geometry = self._select_tube_geometry(
                area_required,
                hot,
                cold,
                tube_passes,
            )
    
            geometry = self._regenerate_geometry(
                geometry,
                tube_passes,
                hot,
            )
    
            bundle_diameter = self._calculate_bundle_diameter(
                geometry["tube_count"],
                geometry["tube_od"],
            )
    
            shell_diameter = self._calculate_shell_diameter(
                bundle_diameter
            )
    
            geometry = self._check_L_over_D(
                geometry,
                shell_diameter,
                tube_passes,
                area_required,
                hot,
            )
    
            # ======================================================
            # VELOCITIES
            # ======================================================
    
            (
                v_tube,
                v_shell,
                tube_count,
                shell_diameter,
                tube_passes,
            ) = self._check_velocities(
                geometry,
                hot,
                cold,
                tube_passes,
                shell_passes,
                shell_diameter,
            )
    
            geometry["tube_count"] = tube_count
    
            geometry = self._regenerate_geometry(
                geometry,
                tube_passes,
                hot,
            )
    
            # ======================================================
            # HTC
            # ======================================================
    
            dimless = self._calculate_dimensionless(
                geometry,
                hot,
                cold,
                v_tube,
                v_shell,
            )
    
            h_t, h_s = self._calculate_htc(
                dimless,
                geometry,
                hot,
                cold,
            )
    
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
    
            # ======================================================
            # DIRTY AREA
            # ======================================================
    
            actual_area = geometry["area"]
    
            required_dirty_area = (
                q_watts
                / max(u_dirty * cltd, 1e-12)
            )
    
            # ======================================================
            # UPDATE STATE
            # ======================================================
    
            state.update({
                "iterations": i,
                "area_required": required_dirty_area,
                "geometry": geometry,
                "bundle_diameter": bundle_diameter,
                "shell_diameter": shell_diameter,
                "v_tube": v_tube,
                "v_shell": v_shell,
                "dimless": dimless,
                "h_t": h_t,
                "h_s": h_s,
                "u_calculated": u_dirty,
                "u_clean": u_clean,
            })
    
            # ======================================================
            # PRESSURE DROP
            # ======================================================
    
            tube_dp_i, shell_dp_i = (
                self._calculate_pressure_drop(
                    hot,
                    cold,
                    shell_passes,
                    tube_passes,
                    shell_diameter,
                    geometry["tube_length"],
                    geometry["tube_id"],
                    v_tube,
                    v_shell,
                )
            )
    
            hard_violations, soft_warnings = (
                self._validate_geometry(
                    state,
                    tube_dp_i,
                    shell_dp_i,
                    hot,
                    cold,
                )
            )
    
            # ======================================================
            # UNDER RELAXATION
            # ======================================================
    
            u_old = state["u_assumed"]
    
            u_new = u_dirty
    
            convergence = abs(
                (u_new - u_old)
                / max(u_old, 1e-12)
            )
    
            print("\n" + "=" * 60)
            print(f"Iteration          : {i}")
            print(f"U_assumed          : {u_old:.4f}")
            print(f"U_dirty            : {u_dirty:.4f}")
            print(f"U_clean            : {u_clean:.4f}")
            print(f"Required Area      : {required_dirty_area:.4f} m2")
            print(f"Actual Area        : {actual_area:.4f} m2")
            print(f"Tube Velocity      : {v_tube:.4f} m/s")
            print(f"Shell Velocity     : {v_shell:.4f} m/s")
            print(f"Tube DP            : {tube_dp_i:.2f} Pa")
            print(f"Shell DP           : {shell_dp_i:.2f} Pa")
            print(f"Convergence Error  : {convergence:.5f}")
            print("=" * 60)
    
            state["u_assumed"] = u_new
    
            # ======================================================
            # CONVERGENCE
            # ======================================================
    
            if (
                convergence < 0.05
                and not hard_violations
            ):
                self._debug(
                    "U iteration converged successfully."
                )
                break
    
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

    def _velocity_warnings(
        self,
        tube_v: float,
        shell_v: float,
        hot: Dict[str, float],
        cold: Dict[str, float],
    ) -> List[str]:
    
        warnings = []
    
        vmin, vmax = self._get_velocity_limits(
            side="tube",
            component=self.hot_in.component,
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
            component=self.cold_in.component,
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
        warnings = list(dict.fromkeys(payload["warnings"]))
        critical: List[str] = []
        advisory: List[str] = []
        for w in warnings:
            wl = w.lower()
            if "pressure drop" in wl or "significantly undersized" in wl or "erosion risk" in wl:
                critical.append(w)
            else:
                advisory.append(w)

        if payload.get("status_override") == "PARTIAL":
            status = "PARTIAL"
        elif "Area significantly undersized — redesign required" in warnings:
            status = "FAILED"
        elif critical:
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
            "tube_length": payload["geometry"]["tube_length"],
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
            "tube_side_fluid": payload.get("assignment", {}).get("tube_side_fluid"),
            "shell_side_fluid": payload.get("assignment", {}).get("shell_side_fluid"),
            "assignment_reason": payload.get("assignment", {}).get("assignment_reason", []),
            "assignment": payload.get("assignment", {}),
        }

    def _design_kern(self) -> Dict[str, Any]:
        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)
        self._warnings = []
        self._validate_inputs(hot, cold)
        assignment = self._assign_fluids_to_sides(hot, cold)

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
        hot_hx = self.hot_in.component.hx_data() if hasattr(self.hot_in.component, "hx_data") else {"u_key": getattr(self.hot_in.component, "hx_type", "generic")}
        cold_hx = self.cold_in.component.hx_data() if hasattr(self.cold_in.component, "hx_data") else {"u_key": getattr(self.cold_in.component, "hx_type", "generic")}
        self._debug(f"Hot hx_data = {hot_hx}")
        self._debug(f"Cold hx_data = {cold_hx}")
        u_range = get_u_range("shell_and_tube", self.service_type, hot_hx.get("u_key", "generic"), cold_hx.get("u_key", "generic"))

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
