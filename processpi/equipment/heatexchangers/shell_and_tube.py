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
        q_kw = self.heat_duty(hot, cold)
        th_in = hot["t_k"]
        tc_in = cold["t_k"]
        #self._debug(f"Hot Cp: {hot["cp"]} Cold Cp {cold["cp"]}")
        if self.hot_out and self.hot_out.temperature and self._safe_float(self.hot_out.temperature.to("C"), "hot_out.temperature") == 25 :
            th_out = self._safe_float(self.hot_out.temperature.to("K"), "hot_out.temperature")
        else:
            th_out = th_in - (q_kw / max(hot["m_dot"] * hot["cp"], 1e-9))

        if self.cold_out and self.cold_out.temperature and self._safe_float(self.cold_out.temperature.to("C"), "cold_out.temperature") == 25:
            #self._debug("Hello World")
            tc_out = self._safe_float(self.cold_out.temperature.to("K"), "cold_out.temperature")
        else:
            tc_out = tc_in + (q_kw / max(cold["m_dot"] * cold["cp"], 1e-9))
            #self._debug(f"tc_out = {tc_in} + ({q_kw}/({cold["m_dot"]}*{cold["cp"]})")
            #self._debug(f"cold_rate: {max(cold["m_dot"] * cold["cp"], 1e-9)}")
        #self._debug(tc_out)
        return q_kw * 1000.0, th_out, tc_out

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

    def _regenerate_geometry(self, geometry: Dict[str, float], tube_passes: int, hot: Dict[str, float] | None = None) -> Dict[str, float]:
        area_per_tube = math.pi * geometry["tube_od"] * geometry["tube_length"]
        geometry["tube_count"] = self._round_tube_count_to_passes(geometry["tube_count"], tube_passes)
        geometry["area"] = geometry["tube_count"] * area_per_tube
        geometry["area_per_tube"] = area_per_tube
        geometry["tube_pitch"] = self._to_float(self.specs.get("tube_pitch"), "m") if self.specs.get("tube_pitch") is not None else (1.25 * geometry["tube_od"])
        geometry["bundle_diameter"] = self._calculate_bundle_diameter(geometry["tube_count"], geometry["tube_od"])
        if "shell_diameter" not in geometry:
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
        tube_od = self._to_float(self.specs.get("tube_od"), "m") if self.specs.get("tube_od") is not None else None
        tube_id = self._to_float(self.specs.get("tube_id"), "m") if self.specs.get("tube_id") is not None else None
        tube_length = self._to_float(self.specs.get("tube_length"), "m") if self.specs.get("tube_length") is not None else None

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
            self._debug("Area Per Tube: ",area_per_tube)
            tube_count = math.ceil(area_required / max(area_per_tube, 1e-12))
            self._debug("Tube Count: ",tube_count)

        # Thermo-hydraulic tube count target: satisfy area and avoid tube-side velocity collapse.
        area_per_tube = math.pi * tube_od * tube_length
        tube_flow_per_tube = math.pi * tube_id**2 / 4.0
        required_count = math.ceil(area_required / max(area_per_tube, 1e-12))
        required_count = self._round_tube_count_to_passes(required_count, tube_passes)
        vmin, vmax = self._get_velocity_limits("tube", self.hot_in.component)
        q_vol_hot = hot["m_dot"] / max(hot["density"], 1e-12)
        low_v_count = int(math.floor((q_vol_hot * tube_passes) / max(vmin * tube_flow_per_tube, 1e-12)))
        high_v_count = int(math.ceil((q_vol_hot * tube_passes) / max(vmax * tube_flow_per_tube, 1e-12)))
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
            geometry = self._regenerate_geometry(geometry, tube_passes, hot)
            self._debug("Geometry :",geometry)
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

    def _regenerate_geometry_state(self, geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float], tube_passes: int, shell_passes: int) -> Dict[str, Any]:
        geometry = self._regenerate_geometry(dict(geometry), tube_passes, hot)
        v_tube, v_shell, tube_count, shell_diameter, tube_passes = self._check_velocities(
            geometry, hot, cold, tube_passes, shell_passes, geometry.get("shell_diameter", 0.5)
        )
        geometry["tube_count"] = tube_count
        geometry["shell_diameter"] = shell_diameter
        geometry = self._regenerate_geometry(geometry, tube_passes, hot)
        dimless = self._calculate_dimensionless(geometry, hot, cold, v_tube, v_shell)
        h_t, h_s = self._calculate_htc(dimless, geometry, hot, cold)
        return {
            "geometry": geometry,
            "v_tube": v_tube,
            "v_shell": v_shell,
            "tube_passes": tube_passes,
            "dimless": dimless,
            "h_t": h_t,
            "h_s": h_s,
        }

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
        self._debug(f"Tube Side Rey:{re_t}, Pra:{pr_t}, Nuss:{nu_t}")
        de_shell = max(1.27 * (geometry["tube_pitch"] ** 2 - 0.785 * geometry["tube_od"] ** 2) / geometry["tube_od"], 1e-6)
        re_s = Reynolds(
            density=cold["density"],
            velocity=v_shell,
            diameter=de_shell,
            viscosity=cold["viscosity"],
        ).calculate()
        pr_s = max(cold["cp"] * 1000 * cold["viscosity"] / max(cold["k"], 1e-12), 1e-12)
        nu_s = KernShellNu(reynolds=max(re_s, 1.0), prandtl=pr_s).calculate()
        self._debug(f"Shell Side Rey:{re_s}, Pra:{pr_s}, Nuss:{nu_s}")
        return {"re_t": re_t, "pr_t": pr_t, "nu_t": nu_t, "de_shell": de_shell, "re_s": re_s, "pr_s": pr_s, "nu_s": nu_s}

    def _calculate_htc(self, dimless: Dict[str, float], geometry: Dict[str, float], hot: Dict[str, float], cold: Dict[str, float]) -> Tuple[float, float]:
        h_t = self._safe_float(ConvectiveH(nusselt=dimless["nu_t"], k=hot["k"], diameter=geometry["tube_id"]).calculate().to("W/m2K"), "h_t")
        h_s = self._safe_float(ConvectiveH(nusselt=dimless["nu_s"], k=cold["k"], diameter=dimless["de_shell"]).calculate().to("W/m2K"), "h_s")
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

        shell_temperature = self._safe_float(self.hot_in.temperature.to("C"), "shell_temperature")
        tube_temperature = self._safe_float(self.cold_in.temperature.to("C"), "tube_temperature")

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
        h_t = h_t * tube_id / tube_od
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
            self._trace_step("THERMAL", "U iteration", i)
            self._trace_step("THERMAL", "Area required", area_required)
    
            # ======================================================
            # GEOMETRY
            # ======================================================
    
            geometry = self._select_tube_geometry(
                area_required,
                hot,
                cold,
                tube_passes,
            )

            regen = self._regenerate_geometry_state(geometry, hot, cold, tube_passes, shell_passes)
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
                    hot=hot,
                    cold=cold,
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
                    hot,
                    cold,
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
    
            state["u_assumed"] = 0.6 * u_old + 0.4 * u_new
            state["u_history"].append(state["u_assumed"])
            state["area_history"].append(actual_area)
            state["geometry_history"].append((geometry["tube_count"], round(geometry["tube_length"],3), round(shell_diameter,3), tube_passes))
            state["convergence_history"].append(convergence_error)
    
            # ======================================================
            # STORE WARNINGS
            # ======================================================
    
            if soft_warnings:
    
                existing = state.get("warnings", [])
    
                existing.extend(soft_warnings)
    
                state["warnings"] = list(dict.fromkeys(existing))

            if "tube_velocity" in hard_violations or "shell_velocity" in hard_violations:
                self._trace_step("OPTIMIZATION", "Geometry rejected", f"hydraulic violation {hard_violations}")
                state["optimization_actions"].append(f"hydraulic_reject:{hard_violations}")
                if not self.fixed_geometry.get("tube_length", False):
                    geometry["tube_length"] = min(12.0, geometry["tube_length"] * 1.10)
                    self._trace_step("OPTIMIZATION", "Action", "increase_tube_length")
                elif tube_passes < 8 and not self.fixed_geometry.get("tube_passes", False):
                    tube_passes = min(8, tube_passes * 2)
                    self._trace_step("OPTIMIZATION", "Action", "increase_tube_passes")
                elif not self.fixed_geometry.get("shell_diameter", False):
                    geometry["shell_diameter"] = max(0.15, geometry["shell_diameter"] * 0.95)
                    self._trace_step("OPTIMIZATION", "Action", "reduce_shell_diameter")
                else:
                    self._warn_with_category("FEASIBILITY_WARNING", "Fixed geometry is hydraulically infeasible")
                    state["status_override"] = "FAILED_CONVERGENCE"
                    break
                continue
    
            if len(state["geometry_history"]) >= 3 and len(set(state["geometry_history"][-3:])) == 1:
                self._warn_with_category("CONVERGENCE_WARNING", "Geometry stagnation detected")
                state["status_override"] = "FAILED_CONVERGENCE"
                break

            # ======================================================
            # CONVERGENCE CHECK
            # ======================================================
    
            if (
                convergence_error < 30.0
                and not hard_violations
            ):
    
                self._debug(
                    f"U iteration converged "
                    f"(error={convergence_error:.2f}%)"
                )
    
                break
    
        return state

      
    def _calculate_pressure_drop(
        self,
        geometry: Dict[str, Any] | None,
        hot: Dict[str, float],
        cold: Dict[str, float],
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
            density=hot["density"],
            velocity=v_tube,
            diameter=tube_id,
            viscosity=hot["viscosity"],
        ).calculate()
    
        if re_tube < 2100:
            f_tube = 16.0 / max(re_tube, 1e-9)
        else:
            f_tube = 0.079 / (re_tube ** 0.25)
    
        tube_dp = (
            4.0
            * f_tube
            * (
                (tube_length * tube_passes)
                / max(tube_id, 1e-9)
            )
            * (
                hot["density"]
                * v_tube**2
                / 2.0
            )
        )
    
        # ==========================================================
        # SHELL SIDE DP
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
    
        # Crossflow area
        as_cross = (
            shell_diameter
            * baffle_spacing
            * (
                (tube_pitch - tube_od)
                / max(tube_pitch, 1e-9)
            )
        )
    
        # Equivalent diameter
        de_shell = (
            1.27
            * (
                tube_pitch**2
                - 0.785 * tube_od**2
            )
            / max(tube_od, 1e-9)
        )
    
        # Shell Reynolds
        re_shell = Reynolds(
            density=cold["density"],
            velocity=v_shell,
            diameter=de_shell,
            viscosity=cold["viscosity"],
        ).calculate()
    
        # ==========================================================
        # IDEAL CROSSFLOW DP
        # ==========================================================
    
        if re_shell < 100:
            j_f = 0.25
        else:
            j_f = 0.0045 + 0.395 / (re_shell ** 0.15)
    
        ncv = max(
            shell_diameter / tube_pitch,
            1.0,
        )
    
        dp_ideal = (
            8.0
            * j_f
            * ncv
            * (
                cold["density"]
                * v_shell**2
                / 2.0
            )
        )
    
        # ==========================================================
        # BELL CORRECTION FACTORS
        # ==========================================================
    
        ab = (
            baffle_spacing
            * max(
                shell_diameter
                - 0.95 * shell_diameter,
                1e-6,
            )
        )
    
        atb = (
            0.0008
            * math.pi
            * tube_od
            * geometry.get("tube_count", 100)
        )
    
        asb = (
            0.003
            * shell_diameter
        )
    
        al = atb + asb
    
        # Bypass factor
        alpha = 5.0 if re_shell < 100 else 4.0
    
        fb = math.exp(
            -alpha
            * (ab / max(as_cross, 1e-9))
        )
    
        # Leakage factor
        if al > 0:
    
            fl = 1.0 - (
                0.44
                * (
                    (atb + 2.0 * asb)
                    / al
                )
            )
    
        else:
    
            fl = 1.0
    
        fl = max(0.4, min(fl, 1.0))
    
        # ==========================================================
        # WINDOW DP
        # ==========================================================
    
        dp_window = (
            0.5
            * cold["density"]
            * v_shell**2
        )
    
        # ==========================================================
        # TOTAL SHELL DP
        # ==========================================================
    
        nbaffles = max(
            int(
                tube_length / baffle_spacing
            ) - 1,
            1,
        )
    
        shell_dp = (
            dp_ideal
            * fb
            * fl
            * nbaffles
        ) + (
            nbaffles
            * dp_window
        )
    
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


        # ==========================================================
        # ENGINEERING INSIGHTS
        # ==========================================================
        
        engineering_insights = []
        
        # ----------------------------------------------------------
        # THERMAL PERFORMANCE
        # ----------------------------------------------------------
        
        u_calc = payload.get("u_calculated", 0.0)
        
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
        
        v_tube = payload.get("v_tube", 0.0)
        
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
        
        v_shell = payload.get("v_shell", 0.0)
        
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
        
        tube_dp = payload.get("tube_dp", 0.0)
        shell_dp = payload.get("shell_dp", 0.0)
        
        tube_dp_limit = self._safe_float(
            self.specs.get("tube_dp", 1e9),
            "tube_dp_limit",
        )
        
        shell_dp_limit = self._safe_float(
            self.specs.get("shell_dp", 1e9),
            "shell_dp_limit",
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
        # OVERALL ASSESSMENT
        # ----------------------------------------------------------
        
        if (
            v_tube < 0.3
            and v_shell < 0.2
        ):
        
            engineering_insights.append(
                "Exchanger appears significantly oversized "
                "for the current operating conditions."
            )
        
        # ----------------------------------------------------------
        # STORE
        # ----------------------------------------------------------
        
        payload["engineering_insights"] = engineering_insights

        return {
            "hx_type": "shell_and_tube",
            "method": payload.get("method", self.method),
            "Q": HeatFlow(payload["q_watts_original"] / 1000.0, "kW"),
            "Area": Area(payload["area"], "m2"),
            "U_assumed": HeatTransferCoefficient(payload["u_assumed"], "W/m2K"),
            "U_user": (HeatTransferCoefficient(payload.get("u_user"), "W/m2K") if payload.get("u_user") is not None else None),
            "U_calculated": HeatTransferCoefficient(payload["u_calculated"], "W/m2K"),
            "LMTD": payload["lmtd"],
            "tube_count": payload["geometry"]["tube_count"],
            "tube_od": Length(payload["geometry"]["tube_od"], "m"),
            "tube_id": Length(payload["geometry"]["tube_id"], "m"),
            "tube_length": Length(payload["geometry"]["tube_length"], "m"),
            "baffle_spacing": Length(max(0.4 * payload["shell_diameter"], 1e-6), "m"),
            "shell_diameter": Length(payload["shell_diameter"], "m"),
            "tube_velocity": Velocity(payload["v_tube"], "m/s"),
            "shell_velocity": Velocity(payload["v_shell"], "m/s"),
            "tube_dp": Pressure(payload["tube_dp"], "Pa"),
            "shell_dp": Pressure(payload["shell_dp"], "Pa"),
            "iterations": payload["iterations"],
            "h_tube": payload.get("h_t"),
            "h_shell": payload.get("h_s"),
            "re_shell": payload.get("re_shell"),
            "status": status,
            "warnings": warnings,
            "tube_side_fluid": payload.get("assignment", {}).get("tube_side_fluid"),
            "shell_side_fluid": payload.get("assignment", {}).get("shell_side_fluid"),
            "assignment_reason": payload.get("assignment", {}).get("assignment_reason", []),
            "assignment": payload.get("assignment", {}),
            "calculation_trace": list(self._calculation_trace),
            "geometry_history": payload.get("geometry_history", []),
            "convergence_history": payload.get("convergence_history", []),
            "optimization_actions": payload.get("optimization_actions", []),
            "warning_details": [{"category": (w.split("]",1)[0][1:] if w.startswith("[") and "]" in w else "GENERAL_WARNING"), "message": (w.split("]",1)[1].strip() if w.startswith("[") and "]" in w else w)} for w in warnings],
            "feasibility_summary": {
                "hydraulic_ok": payload.get("v_tube", 0.0) > 0 and payload.get("v_shell", 0.0) > 0,
                "pressure_drop_ok": payload.get("tube_dp", 0.0) <= self._dp_limit({"phase":"liquid","viscosity":1e-3,"p_bar":1.0}) and payload.get("shell_dp", 0.0) <= self._dp_limit({"phase":"liquid","viscosity":1e-3,"p_bar":1.0}),
                "status": status,
            },
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
        self._trace_step("THERMAL", "Heat duty (W)", q_watts)
        lmtd = self._calculate_lmtd(hot, cold, th_out, tc_out)
        self._trace_step("THERMAL", "LMTD", lmtd)

        shell_passes, tube_passes, ft = self._adjust_passes(hot, cold, th_out, tc_out)
        self._trace_step("THERMAL", "Ft", ft)
        self._trace_step("GEOMETRY", "Shell passes", shell_passes)
        self._trace_step("GEOMETRY", "Tube passes", tube_passes)
        warnings: List[str] = list(getattr(self, "_warnings", []))

        n_units = 1
        effective_q_watts = q_watts
        if ft < 0.78:
            n_units = int(math.ceil(0.78 / max(ft, 1e-6)))
            effective_q_watts = q_watts / n_units
            warnings.append(f"Using {n_units} exchangers in series to satisfy Ft requirement")

        cltd = max(ft * lmtd, 1e-9)
        self._debug(cltd)

        u_assumed = self._assume_u(hot, cold)
        self._trace_step("THERMAL", "U assumed initial", u_assumed)
        hot_hx = self.hot_in.component.hx_data() if hasattr(self.hot_in.component, "hx_data") else {"u_key": getattr(self.hot_in.component, "hx_type", "generic")}
        cold_hx = self.cold_in.component.hx_data() if hasattr(self.cold_in.component, "hx_data") else {"u_key": getattr(self.cold_in.component, "hx_type", "generic")}
        self._debug(f"Hot hx_data = {hot_hx}")
        self._debug(f"Cold hx_data = {cold_hx}")
        u_range = get_u_range("shell_and_tube", self.service_type, hot_hx.get("u_key", "generic"), cold_hx.get("u_key", "generic"))

        state = self._iterate_U(effective_q_watts, cltd, hot, cold, shell_passes, tube_passes, u_assumed, u_range)

        if state["shell_diameter"] > 1.5:
            warnings.append("Shell diameter too large → consider multi-shell exchanger")

        tube_dp, shell_dp = (
            self._calculate_pressure_drop(
                hot=hot,
                cold=cold,
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

        tube_limit_val = self.specs.get("tube_dp", self._dp_limit(hot))
        shell_limit_val = self.specs.get("shell_dp", self._dp_limit(cold))
        tube_limit = self._safe_float(tube_limit_val.to("Pa"), "tube_dp_limit") if hasattr(tube_limit_val, "to") else self._safe_float(tube_limit_val, "tube_dp_limit")
        shell_limit = self._safe_float(shell_limit_val.to("Pa"), "shell_dp_limit") if hasattr(shell_limit_val, "to") else self._safe_float(shell_limit_val, "shell_dp_limit")

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
    
        data["U_calculated"] = (
            u_results["U_dirty"]
        )
    
        data["U_clean"] = (
            u_results["U_clean"]
        )
    
        data["bell_factors"] = {
            "Fn": fn,
            "Fw": fw,
            "Fb": fb,
            "Fl": fl,
            "Fs": fs,
        }
    
        # ======================================================
        # OPTIONAL:
        # Increase shell DP slightly for Bell realism
        # ======================================================
    
        data["shell_dp"] = self._get_value(data["shell_dp"], name="shell_dp") * 1.15
    
        return data
    def rate(self) -> Dict[str, Any]:
    
        """
        Universal intelligent rating engine for ProcessPI heat exchangers.
        """
    
        import math
    
        self._warnings = []
        recommendations = []
    
        # ==========================================================
        # VALIDATE STREAMS
        # ==========================================================
    
        if self.hot_in is None:
            raise ValueError("Hot stream is mandatory")
    
        if self.cold_in is None:
            raise ValueError("Cold stream is mandatory")
    
        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)
    
        self._validate_inputs(hot, cold)
    
        assignment = self._assign_fluids_to_sides(hot, cold)
    
        # ==========================================================
        # SERVICE IDENTIFICATION
        # ==========================================================
    
        if hot["phase"] == "vapor":
    
            self.service_type = "condenser"
    
        elif cold["phase"] == "vapor":
    
            self.service_type = "reboiler"
    
        elif hot["t_k"] > cold["t_k"]:
    
            self.service_type = "cooler"
    
        else:
    
            self.service_type = "heater"
    
        # ==========================================================
        # DUTY
        # ==========================================================
    
        if self.service_type in ["condenser", "reboiler"]:
    
            latent_heat = self._safe_float(
                self.specs.get("latent_heat", 2257000.0),
                "latent_heat",
            )
    
            q_actual = hot["m_dot"] * latent_heat
    
        else:
    
            Ch = hot["m_dot"] * hot["cp"] * 1000.0
            Cc = cold["m_dot"] * cold["cp"] * 1000.0
    
            q_hot = Ch * abs(
                hot.get("t_in_k", hot["t_k"])
                - hot.get("t_out_k", hot["t_k"] - 10.0)
            )
    
            q_cold = Cc * abs(
                cold.get("t_out_k", cold["t_k"] + 10.0)
                - cold.get("t_in_k", cold["t_k"])
            )
    
            q_actual = min(q_hot, q_cold)
    
        # ==========================================================
        # USER U / ASSUMED U
        # ==========================================================
    
        user_u = self.specs.get("U")
    
        if user_u is not None:
    
            if hasattr(user_u, "to"):
                u_dirty = self._safe_float(
                    user_u.to("W/m2K"),
                    "U",
                )
            else:
                u_dirty = self._safe_float(user_u, "U")
    
            u_clean = u_dirty * 1.15
    
            u_source = "user"
    
        else:
    
            hot_hx = (
                self.hot_in.component.hx_data()
                if hasattr(self.hot_in.component, "hx_data")
                else {"u_key": "generic"}
            )
    
            cold_hx = (
                self.cold_in.component.hx_data()
                if hasattr(self.cold_in.component, "hx_data")
                else {"u_key": "generic"}
            )
    
            u_range = get_u_range(
                "shell_and_tube",
                self.service_type,
                hot_hx.get("u_key", "generic"),
                cold_hx.get("u_key", "generic"),
            )
    
            u_dirty = 0.5 * (u_range[0] + u_range[1])
    
            u_clean = u_dirty * 1.15
    
            u_source = "assumed"
    
        # ==========================================================
        # TEMPERATURE PROFILE
        # ==========================================================
    
        th_in = hot["t_k"]
        tc_in = cold["t_k"]
    
        # ----------------------------------------------------------
        # CONDENSER / REBOILER STABILIZATION
        # ----------------------------------------------------------
    
        if self.service_type in ["condenser", "reboiler"]:
    
            condensing_temp = hot["t_k"]
    
            th_out = condensing_temp - 2.0
    
            th_in = condensing_temp + 2.0
    
            Cc = cold["m_dot"] * cold["cp"] * 1000.0
    
            tc_out = tc_in + q_actual / max(Cc, 1e-12)
    
        else:
    
            Ch = hot["m_dot"] * hot["cp"] * 1000.0
            Cc = cold["m_dot"] * cold["cp"] * 1000.0
    
            th_out = th_in - q_actual / max(Ch, 1e-12)
    
            tc_out = tc_in + q_actual / max(Cc, 1e-12)
    
        # ==========================================================
        # LMTD
        # ==========================================================
    
        lmtd = self._calculate_lmtd(
            hot,
            cold,
            th_out,
            tc_out,
        )
    
        ft = float(self.specs.get("ft", 1.0))
    
        cltd = max(ft * lmtd, 1e-9)
    
        # ==========================================================
        # AREA
        # ==========================================================
    
        provided_area = self.specs.get("area")
    
        if provided_area is not None:
    
            if hasattr(provided_area, "to"):
    
                area = self._safe_float(
                    provided_area.to("m2"),
                    "area",
                )
    
            else:
    
                area = self._safe_float(
                    provided_area,
                    "area",
                )
    
            area_source = "provided"
    
        else:
    
            area = q_actual / max(u_dirty * cltd, 1e-12)
    
            area_source = "calculated"
    
        # ==========================================================
        # GEOMETRY
        # ==========================================================
    
        tube_od = self._safe_float(
            self.specs.get("tube_od", 0.01905),
            "tube_od",
        )
    
        tube_id = self._safe_float(
            self.specs.get("tube_id", 0.016),
            "tube_id",
        )
    
        tube_length = self._safe_float(
            self.specs.get("tube_length", 6.0),
            "tube_length",
        )
    
        tube_pitch = self._safe_float(
            self.specs.get("tube_pitch", 1.25 * tube_od),
            "tube_pitch",
        )
    
        tube_passes = int(self.specs.get("tube_passes", 2))
    
        shell_passes = int(self.specs.get("shell_passes", 1))
    
        # ----------------------------------------------------------
    
        if self.specs.get("tube_count") is not None:
    
            tube_count = int(self.specs["tube_count"])
    
        else:
    
            tube_count = max(
                1,
                int(
                    area
                    / (
                        math.pi
                        * tube_od
                        * tube_length
                    )
                ),
            )
    
            recommendations.append(
                "Tube count estimated from required area"
            )
    
        # ----------------------------------------------------------
    
        if self.specs.get("shell_diameter") is not None:
    
            shell_diameter = self._safe_float(
                self.specs["shell_diameter"],
                "shell_diameter",
            )
    
        else:
    
            shell_diameter = max(
                0.1,
                0.637
                * (
                    (
                        tube_count
                        * tube_pitch**2
                    ) / 0.785
                )**0.5,
            )
    
            recommendations.append(
                "Shell diameter estimated from bundle geometry"
            )
    
        # ----------------------------------------------------------
    
        baffle_spacing = self._safe_float(
            self.specs.get(
                "baffle_spacing",
                0.4 * shell_diameter,
            ),
            "baffle_spacing",
        )
    
        geometry = {
    
            "tube_od": tube_od,
            "tube_id": tube_id,
            "tube_length": tube_length,
            "tube_count": tube_count,
            "tube_pitch": tube_pitch,
            "shell_diameter": shell_diameter,
            "baffle_spacing": baffle_spacing,
    
        }
    
        # ==========================================================
        # GEOMETRY VALIDATION
        # ==========================================================
    
        geometry_valid = True
    
        if tube_pitch < 1.25 * tube_od:
    
            geometry_valid = False
    
            self._warnings.append(
                "[MECHANICAL_WARNING] Tube pitch below TEMA minimum"
            )
    
        # ==========================================================
        # FLOW HYDRAULICS
        # ==========================================================
    
        q_vol_hot = (
            hot["m_dot"]
            / max(hot["density"], 1e-12)
        )
    
        q_vol_cold = (
            cold["m_dot"]
            / max(cold["density"], 1e-12)
        )
    
        # ----------------------------------------------------------
        # TUBE SIDE
        # ----------------------------------------------------------
    
        tube_flow_area = (
    
            (tube_count / tube_passes)
    
            * (
    
                math.pi
                * tube_id**2
                / 4.0
    
            )
        )
    
        v_tube = (
            q_vol_hot
            / max(tube_flow_area, 1e-12)
        )
    
        # ----------------------------------------------------------
        # SHELL SIDE
        # ----------------------------------------------------------
    
        shell_flow_area = (
    
            shell_diameter
    
            * baffle_spacing
    
            * (
    
                (tube_pitch - tube_od)
                / max(tube_pitch, 1e-12)
    
            )
    
            * 0.62
        )
    
        v_shell = (
            q_vol_cold
            / max(shell_flow_area, 1e-12)
        )
    
        # ==========================================================
        # DIMENSIONLESS
        # ==========================================================
    
        de_shell = (
    
            1.10
    
            * (
    
                tube_pitch**2
                - 0.917 * tube_od**2
    
            )
    
            / max(tube_od, 1e-12)
    
        )
    
        dimless = self._calculate_dimensionless(
            geometry,
            hot,
            cold,
            v_tube,
            v_shell,
        )
    
        dimless["de_shell"] = de_shell
    
        # ==========================================================
        # HTC
        # ==========================================================
    
        h_t, h_s = self._calculate_htc(
            dimless,
            geometry,
            hot,
            cold,
        )
    
        # ==========================================================
        # OVERALL U
        # ==========================================================
    
        # IMPORTANT:
        # Do NOT overwrite user U in rate mode
    
        if u_source != "user":
    
            u_results = self._calculate_overall_U(
    
                h_t=h_t,
    
                h_s=h_s,
    
                geometry=geometry,
    
                u_range=(u_dirty, u_clean),
    
            )
    
            u_dirty = u_results["U_dirty"]
    
            u_clean = u_results["U_clean"]
    
        # ==========================================================
        # PRESSURE DROP
        # ==========================================================
    
        tube_dp, shell_dp = self._calculate_pressure_drop(
    
            geometry=geometry,
    
            hot=hot,
    
            cold=cold,
    
            shell_velocity=v_shell,
    
            tube_velocity=v_tube,
    
            shell_passes=shell_passes,
    
            tube_passes=tube_passes,
    
            shell_diameter=shell_diameter,
    
            tube_length=tube_length,
    
            tube_id=tube_id,
    
            orientation=self.specs.get(
                "orientation",
                "horizontal",
            ),
        )
    
        # ==========================================================
        # CONSTRAINTS
        # ==========================================================
    
        tube_velocity_ok = (
            0.5 <= v_tube <= 3.0
        )
    
        shell_velocity_ok = (
            0.3 <= v_shell <= 2.0
        )
    
        tube_dp_limit = self._safe_float(
            self.specs.get("tube_dp", 70000.0),
            "tube_dp_limit",
        )
    
        shell_dp_limit = self._safe_float(
            self.specs.get("shell_dp", 14000.0),
            "shell_dp_limit",
        )
    
        pressure_drop_ok = (
    
            tube_dp <= tube_dp_limit
    
            and
    
            shell_dp <= shell_dp_limit
    
        )
    
        thermal_feasible = area > 0.0
    
        hydraulic_feasible = (
    
            tube_velocity_ok
            and shell_velocity_ok
            and pressure_drop_ok
    
        )
    
        # ==========================================================
        # WARNINGS
        # ==========================================================
    
        if not tube_velocity_ok:
    
            self._warnings.append(
                "[HYDRAULIC_WARNING] Tube velocity outside recommended range"
            )
    
        if not shell_velocity_ok:
    
            self._warnings.append(
                "[HYDRAULIC_WARNING] Shell velocity outside recommended range"
            )
    
        if not pressure_drop_ok:
    
            self._warnings.append(
                "[PRESSURE_DROP_WARNING] Pressure drop exceeds allowable limits"
            )
    
        # ==========================================================
        # ENGINEERING ASSESSMENT
        # ==========================================================
    
        score = 100
    
        if not geometry_valid:
            score -= 20
    
        if not tube_velocity_ok:
            score -= 10
    
        if not shell_velocity_ok:
            score -= 10
    
        if not pressure_drop_ok:
            score -= 20
    
        if score >= 90:
    
            assessment = "EXCELLENT"
    
        elif score >= 75:
    
            assessment = "ACCEPTABLE"
    
        elif score >= 60:
    
            assessment = "MARGINAL"
    
        else:
    
            assessment = "NOT_RECOMMENDED"
    
        # ==========================================================
        # PAYLOAD
        # ==========================================================
    
        payload = {
    
            "method": self.method,
    
            "service": self.service_type,
    
            "q_watts_original": q_actual,
    
            "q_watts_effective": q_actual,
    
            "lmtd": lmtd,
    
            "cltd": cltd,
    
            "ft": ft,
    
            "u_assumed": u_dirty,
    
            "u_calculated": u_dirty,
    
            "u_clean": u_clean,
    
            "u_user": (
                u_dirty
                if u_source == "user"
                else None
            ),
    
            "u_source": u_source,
    
            "area": area,
    
            "area_source": area_source,
    
            "geometry": geometry,
    
            "shell_diameter": shell_diameter,
    
            "bundle_diameter": self._calculate_bundle_diameter(
                tube_count,
                tube_od,
            ),
    
            "tube_passes": tube_passes,
    
            "shell_passes": shell_passes,
    
            "th_out": th_out,
    
            "tc_out": tc_out,
    
            "h_t": h_t,
    
            "h_s": h_s,
    
            "dimless": dimless,
    
            "v_tube": v_tube,
    
            "v_shell": v_shell,
    
            "tube_dp": tube_dp,
    
            "shell_dp": shell_dp,
    
            "thermal_feasible": thermal_feasible,
    
            "hydraulic_feasible": hydraulic_feasible,
    
            "pressure_drop_feasible": pressure_drop_ok,
    
            "geometry_valid": geometry_valid,
    
            "engineering_assessment": assessment,
    
            "feasibility_score": score,
    
            "warnings": self._warnings,
    
            "recommendations": recommendations,
    
            "assignment": assignment,
    
            "iterations": 1,
    
            "optimization_actions": [],
    
            "geometry_history": [],
    
            "convergence_history": [],
    
            "warning_details": [],
    
            "phase_change": (
                self.service_type
                in ["condenser", "reboiler"]
            ),
    
            "orientation": self.specs.get(
                "orientation",
                "horizontal",
            ),
        }
    
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
