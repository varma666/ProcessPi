from __future__ import annotations

import math
from typing import Any, Dict, List

from processpi.calculations.fluids import FluidVelocity
from processpi.calculations.heat_transfer.hx_kern import (
    ConvectiveH,
    DarcyDrop,
    DittusBoelter,
    KernShellNu,
    Reynolds,
    ShellDiameterEstimate,
    TubeCountFromArea,
)

from .base import HeatExchanger
from .standards import get_u_range


class ShellAndTubeHX(HeatExchanger):
    def _assume_u(self, hot: Dict[str, float], cold: Dict[str, float]) -> float:
        if self.specs.get("U") is not None:
            return float(self.specs["U"].to("W/m2K").value)
        hot_type = getattr(self.hot_in.component, "hx_type", "generic")
        cold_type = getattr(self.cold_in.component, "hx_type", "generic")
        service_type = getattr(self, "service_type", "heat_exchanger")
        u_range = get_u_range("shell_and_tube", service_type, hot_type, cold_type)
        if u_range:
            u_min, u_max = u_range
            return 0.5 * (u_min + u_max)
        return 300.0

    def _velocity_warnings(self, tube_v: float, shell_v: float, hot: Dict[str, float], cold: Dict[str, float]) -> List[str]:
        warnings: List[str] = []
        tube_target = (1.5, 2.5) if (self.hot_in.component and getattr(self.hot_in.component, "name", "").lower() == "water") else (1.0, 2.0)
        if not (tube_target[0] <= tube_v <= tube_target[1]):
            warnings.append(f"Tube velocity {tube_v:.2f} m/s outside recommended {tube_target[0]}-{tube_target[1]} m/s")

        if cold["phase"] == "vapor":
            p = cold["p_bar"]
            target = (50, 70) if p < 1 else ((10, 30) if p <= 2 else (5, 10))
        else:
            target = (0.3, 1.0)
        if not (target[0] <= shell_v <= target[1]):
            warnings.append(f"Shell velocity {shell_v:.2f} m/s outside recommended {target[0]}-{target[1]} m/s")
        return warnings

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

    def design(self) -> Dict[str, Any]:
        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)

        if hot["phase"] == "vapor":
            self.service_type = "condenser"
        elif cold["phase"] == "vapor":
            self.service_type = "vaporizer"
        elif hot["t_k"] > cold["t_k"]:
            self.service_type = "cooler"
        else:
            self.service_type = "heater"

        q_w = self.heat_duty(hot, cold)

        shell_passes = int(self.specs.get("shell_passes", 1))
        tube_passes = int(self.specs.get("tube_passes", 2))
        tube_od = float(self.specs.get("tube_od", 0.019))
        tube_id = float(self.specs.get("tube_id", 0.016))
        tube_length = float(self.specs.get("tube_length", 5.0))
        tube_pitch = float(self.specs.get("tube_pitch", 1.25 * tube_od))

        # Temperatures
        th_in = hot["t_k"]
        tc_in = cold["t_k"]

        if self.hot_out and self.hot_out.temperature:
            th_out = self.hot_out.temperature.to("K").value
        else:
            th_out = th_in - q_w / max(hot["m_dot"] * hot["cp"], 1e-9)

        if self.cold_out and self.cold_out.temperature:
            tc_out = self.cold_out.temperature.to("K").value
        else:
            tc_out = tc_in + q_w / max(cold["m_dot"] * cold["cp"], 1e-9)

        dtlm = self.lmtd(th_in, th_out, tc_in, tc_out)

        u_assumed = self._assume_u(hot, cold)
        hot_type = getattr(self.hot_in.component, "hx_type", "generic")
        cold_type = getattr(self.cold_in.component, "hx_type", "generic")
        u_range = get_u_range("shell_and_tube", self.service_type, hot_type, cold_type)

        iterations = 0
        warnings: List[str] = []

        while iterations < 25:
            iterations += 1

            # --- STEP 1: Thermal Area Requirement ---
            q_watts = q_w * 1000
            print(u_assumed)
            area_required = q_watts / max(u_assumed * dtlm, 1e-6)

            # --- STEP 2: Tube-side velocity design ---
            v_target = float(self.specs.get("tube_velocity_target", 1.5))
            q_vol_hot = hot["m_dot"] / hot["density"]
            q_vol_cold = cold["m_dot"] / cold["density"]

            flow_area_required = q_vol_hot / max(v_target, 1e-6)
            area_per_tube_flow = math.pi * tube_id**2 / 4.0

            tube_count_velocity = int(flow_area_required / max(area_per_tube_flow, 1e-12) * tube_passes)

            # --- STEP 3: Thermal tube requirement ---
            area_per_tube_surface = math.pi * tube_od * tube_length
            tube_count_thermal = math.ceil(area_required / max(area_per_tube_surface, 1e-12))

            # --- FINAL tube count ---
            from .standards import select_standard_exchanger
            
            # --- STEP 3: preliminary tube count ---
            tube_count_calc = max(tube_count_velocity, tube_count_thermal, 10)
            
            # --- STEP 4: select standard exchanger ---
            selected = select_standard_exchanger(
                                                    area_required,
                                                    tube_length,
                                                    tube_passes,
                                                    hot["m_dot"],
                                                    hot["density"],
                                                    cold["m_dot"],
                                                    cold["density"],
                                                    tube_id
                                                )
            
            if selected:
                tube_count = selected["n"]
                shell_diameter = selected["Da"]
                area = selected["AS"] * tube_length
            else:
                # fallback (rare)
                tube_count = tube_count_calc
                area = tube_count * math.pi * tube_od * tube_length
                shell_diameter = math.sqrt(4 * required_shell_area / math.pi)
            print("AREA REQUIRED:", area_required)
            print("SELECTED:", selected)
            baffle_spacing = float(
                self.specs.get(
                    "baffle_spacing",
                    max(0.3 * shell_diameter, min(0.5 * shell_diameter, 0.45 * shell_diameter))
                )
            )

            # --- Velocities ---
            tube_area_flow = max(tube_count / tube_passes * area_per_tube_flow, 1e-12)
            v_tube = q_vol_hot / max(tube_area_flow, 1e-12)

            shell_area_flow = math.pi * shell_diameter**2 / 4.0
            v_shell = q_vol_cold / max(shell_area_flow, 1e-12)

            # --- Heat transfer coefficients ---
            re_t = Reynolds(density=hot["density"], velocity=v_tube, diameter=tube_id, viscosity=hot["viscosity"]).calculate()
            pr_t = max(hot["cp"] * hot["viscosity"] / max(hot["k"], 1e-12), 1e-12)
            nu_t = DittusBoelter(reynolds=max(re_t, 1.0), prandtl=pr_t, n=0.4).calculate()
            h_t = ConvectiveH(nusselt=nu_t, k=hot["k"], diameter=tube_id).calculate().to("W/m2K").value

            de_shell = max(1.27 * (tube_pitch**2 - 0.785 * tube_od**2) / tube_od, 1e-6)
            re_s = Reynolds(density=cold["density"], velocity=v_shell, diameter=de_shell, viscosity=cold["viscosity"]).calculate()
            pr_s = max(cold["cp"] * cold["viscosity"] / max(cold["k"], 1e-12), 1e-12)
            nu_s = KernShellNu(reynolds=max(re_s, 1.0), prandtl=pr_s).calculate()
            h_s = ConvectiveH(nusselt=nu_s, k=cold["k"], diameter=de_shell).calculate().to("W/m2K").value

            u_calculated = self.overall_u(
                h_tube=h_t,
                h_shell=h_s,
                fouling_factor=float(self.specs.get("fouling_factor", 0.0))
            )
            u_min, u_max = u_range if u_range else (100, 1000)
            u_calculated = max(min(u_calculated, u_max), u_min)

            # --- Convergence check ---
            if abs((u_calculated - u_assumed) / max(u_assumed, 1e-6)) < 0.30:
                break

            u_assumed = u_calculated

        # --- Pressure drop ---
        f_tube = float(self.specs.get("f_tube", 0.005))
        f_shell = float(self.specs.get("f_shell", 0.02))

        tube_dp = DarcyDrop(
            f=f_tube,
            length=tube_length * tube_passes,
            diameter=tube_id,
            density=hot["density"],
            velocity=v_tube
        ).calculate().to("Pa").value

        shell_dp = DarcyDrop(
            f=f_shell,
            length=max(shell_passes, 1) * shell_diameter,
            diameter=max(shell_diameter, 1e-6),
            density=cold["density"],
            velocity=v_shell
        ).calculate().to("Pa").value

        # --- Limits ---
        tube_limit = float(self.specs.get("tube_dp", self._dp_limit(hot)).to("Pa").value)
        shell_limit = float(self.specs.get("shell_dp", self._dp_limit(cold)).to("Pa").value)

        if tube_dp > tube_limit:
            warnings.append(f"Tube-side pressure drop {tube_dp:.1f} Pa exceeds limit {tube_limit:.1f} Pa")
        if shell_dp > shell_limit:
            warnings.append(f"Shell-side pressure drop {shell_dp:.1f} Pa exceeds limit {shell_limit:.1f} Pa")

        # --- Velocity warnings ---
        warnings.extend(self._velocity_warnings(v_tube, v_shell, hot, cold))

        # --- Thermal safety ---
        if area < area_required:
            warnings.append("Heat transfer area insufficient")

        if area < area_required:
            warnings.append("Selected standard exchanger undersized → next size required")

        status = "OK" if (not warnings and iterations < 25) else "VIOLATION"

        return {
            "hx_type": "shell_and_tube",
            "Q": q_w,
            "Area": area,
            "U_assumed": u_assumed,
            "U_calculated": u_calculated,
            "LMTD": dtlm,
            "tube_count": tube_count,
            "shell_diameter": shell_diameter,
            "tube_velocity": v_tube,
            "shell_velocity": v_shell,
            "tube_dp": tube_dp,
            "shell_dp": shell_dp,
            "iterations": iterations,
            "status": status,
            "warnings": warnings,
        }
