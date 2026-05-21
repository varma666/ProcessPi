from __future__ import annotations

import math

from typing import Any, Dict

from .base import HeatExchanger


class DoublePipeHX(HeatExchanger):

    def _velocity_targets(self) -> dict[str, float]:
        return {
            "tube_min": float(self.specs.get("tube_velocity_min", 0.5)),
            "tube_max": float(self.specs.get("tube_velocity_max", 2.5)),
            "annulus_min": float(self.specs.get("annulus_velocity_min", 0.3)),
            "annulus_max": float(self.specs.get("annulus_velocity_max", 2.0)),
        }

    def _compute_parallel_paths(self, tube_velocity: float, annulus_velocity: float) -> int:
        limits = self._velocity_targets()
        n_tube = max(1, math.ceil(tube_velocity / max(limits["tube_max"], 1e-6)))
        n_annulus = max(1, math.ceil(annulus_velocity / max(limits["annulus_max"], 1e-6)))
        return max(n_tube, n_annulus)

    # ==========================================================
    # DESIGN MODE
    # ==========================================================

    def design(self) -> Dict[str, Any]:

        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)

        q = self.heat_duty(hot, cold)

        # ======================================================
        # OUTLET TEMPERATURES
        # ======================================================

        th_out = (
            self._safe_float(self.hot_out.temperature.to("K"), "hot_out.temperature")
            if (
                self.hot_out
                and self.hot_out.temperature
            )
            else (
                hot["t_k"]
                - q / (
                    hot["m_dot"]
                    * hot["cp"]
                    * 1000.0
                )
            )
        )

        tc_out = (
            self._safe_float(self.cold_out.temperature.to("K"), "cold_out.temperature")
            if (
                self.cold_out
                and self.cold_out.temperature
            )
            else (
                cold["t_k"]
                + q / (
                    cold["m_dot"]
                    * cold["cp"]
                    * 1000.0
                )
            )
        )

        # ======================================================
        # LMTD
        # ======================================================

        lmtd = self.lmtd(
            hot["t_k"],
            th_out,
            cold["t_k"],
            tc_out,
        )

        # ======================================================
        # U
        # ======================================================

        u_spec = self.specs.get("U", 350.0)
        u_assumed = self._safe_float(u_spec.to("W/m2K"), "U") if hasattr(u_spec, "to") else self._safe_float(u_spec, "U")

        # ======================================================
        # AREA
        # ======================================================

        area_required = self.area(
            q * 1000.0,
            u_assumed,
            lmtd,
        )

        area = float(
            self.specs.get(
                "area",
                area_required,
            )
        )

        # ======================================================
        # GEOMETRY
        # ======================================================

        tube_od = float(
            self.specs.get(
                "tube_od",
                0.0254,
            )
        )

        tube_id = float(
            self.specs.get(
                "tube_id",
                0.021,
            )
        )

        tube_length = float(
            self.specs.get(
                "tube_length",
                6.0,
            )
        )

        annulus_diameter = float(
            self.specs.get(
                "annulus_diameter",
                0.05,
            )
        )

        # ======================================================
        # VELOCITIES
        # ======================================================

        tube_area = (
            math.pi
            * tube_id**2
            / 4.0
        )

        annulus_area = (
            math.pi
            * (
                annulus_diameter**2
                - tube_od**2
            )
            / 4.0
        )

        tube_velocity_single = (
            cold["m_dot"]
            / (
                cold["density"]
                * tube_area
            )
        )

        annulus_velocity_single = (
            hot["m_dot"]
            / (
                hot["density"]
                * annulus_area
            )
        )

        parallel_paths = self._compute_parallel_paths(tube_velocity_single, annulus_velocity_single)
        tube_velocity = tube_velocity_single / parallel_paths
        annulus_velocity = annulus_velocity_single / parallel_paths

        # ======================================================
        # PRESSURE DROP
        # ======================================================

        friction_factor_tube = float(self.specs.get("tube_friction_factor", 0.02))
        friction_factor_annulus = float(self.specs.get("annulus_friction_factor", 0.03))
        tube_dp = friction_factor_tube * (tube_length / max(tube_id, 1e-6)) * (cold["density"] * tube_velocity**2 / 2.0)

        hydraulic_diameter = max(annulus_diameter - tube_od, 1e-6)
        annulus_dp = friction_factor_annulus * (tube_length / hydraulic_diameter) * (hot["density"] * annulus_velocity**2 / 2.0)

        # ======================================================
        # RESULTS
        # ======================================================

        return {
            "hx_type": "double_pipe",
            "method": "basic",
            "Q": q,
            "Area": area,
            "U_assumed": u_assumed,
            "U_clean": u_assumed,
            "U_dirty": u_assumed,
            "U_calculated": u_assumed,
            "LMTD": lmtd,
            "tube_count": parallel_paths,
            "parallel_paths": parallel_paths,
            "tube_od": tube_od,
            "tube_id": tube_id,
            "tube_length": tube_length,
            "shell_diameter": annulus_diameter,
            "tube_velocity": tube_velocity,
            "shell_velocity": annulus_velocity,
            "tube_dp": tube_dp,
            "shell_dp": annulus_dp,
            "iterations": 1,
            "status": "OK",
            "warnings": self._double_pipe_warnings(tube_velocity, annulus_velocity),
        }

    def _double_pipe_warnings(self, tube_velocity: float, annulus_velocity: float) -> list[str]:
        limits = self._velocity_targets()
        warnings: list[str] = []
        if tube_velocity < limits["tube_min"]:
            warnings.append("[HYDRAULIC_WARNING] Tube velocity below recommended range for double-pipe exchanger")
        elif tube_velocity > limits["tube_max"]:
            warnings.append("[HYDRAULIC_WARNING] Tube velocity above recommended range for double-pipe exchanger")
        if annulus_velocity < limits["annulus_min"]:
            warnings.append("[HYDRAULIC_WARNING] Annulus velocity below recommended range for double-pipe exchanger")
        elif annulus_velocity > limits["annulus_max"]:
            warnings.append("[HYDRAULIC_WARNING] Annulus velocity above recommended range for double-pipe exchanger")
        return warnings

    # ==========================================================
    # RATE MODE
    # ==========================================================

    def rate(self) -> Dict[str, Any]:

        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)

        # ======================================================
        # GEOMETRY
        # ======================================================

        tube_od = float(
            self.specs["tube_od"]
        )

        tube_id = float(
            self.specs["tube_id"]
        )

        tube_length = float(
            self.specs["tube_length"]
        )

        annulus_diameter = float(
            self.specs["annulus_diameter"]
        )

        area = float(
            self.specs["area"]
        )

        # ======================================================
        # FLOW AREAS
        # ======================================================

        tube_area = (
            math.pi
            * tube_id**2
            / 4.0
        )

        annulus_area = (
            math.pi
            * (
                annulus_diameter**2
                - tube_od**2
            )
            / 4.0
        )

        # ======================================================
        # VELOCITIES
        # ======================================================

        tube_velocity_single = (
            cold["m_dot"]
            / (
                cold["density"]
                * tube_area
            )
        )

        annulus_velocity_single = (
            hot["m_dot"]
            / (
                hot["density"]
                * annulus_area
            )
        )
        parallel_paths = int(self.specs.get("parallel_paths", self._compute_parallel_paths(tube_velocity_single, annulus_velocity_single)))
        tube_velocity = tube_velocity_single / parallel_paths
        annulus_velocity = annulus_velocity_single / parallel_paths

        # ======================================================
        # HEAT TRANSFER COEFFICIENTS
        # ======================================================

        re_tube = (
            cold["density"]
            * tube_velocity
            * tube_id
            / cold["viscosity"]
        )

        pr_tube = (
            cold["cp"]
            * 1000.0
            * cold["viscosity"]
            / cold["k"]
        )

        nu_tube = (
            0.023
            * re_tube**0.8
            * pr_tube**0.4
        )

        h_tube = (
            nu_tube
            * cold["k"]
            / tube_id
        )

        hydraulic_diameter = (
            annulus_diameter
            - tube_od
        )

        re_annulus = (
            hot["density"]
            * annulus_velocity
            * hydraulic_diameter
            / hot["viscosity"]
        )

        pr_annulus = (
            hot["cp"]
            * 1000.0
            * hot["viscosity"]
            / hot["k"]
        )

        nu_annulus = (
            0.023
            * re_annulus**0.8
            * pr_annulus**0.4
        )

        h_annulus = (
            nu_annulus
            * hot["k"]
            / hydraulic_diameter
        )

        # ======================================================
        # OVERALL U
        # ======================================================

        r_total = (
            (1 / h_tube)
            + (1 / h_annulus)
        )

        u_dirty = 1.0 / r_total

        # ======================================================
        # UA
        # ======================================================

        UA = (
            u_dirty
            * area
        )

        # ======================================================
        # NTU
        # ======================================================

        Ch = (
            hot["m_dot"]
            * hot["cp"]
            * 1000.0
        )

        Cc = (
            cold["m_dot"]
            * cold["cp"]
            * 1000.0
        )

        Cmin = min(Ch, Cc)

        Cmax = max(Ch, Cc)

        Cr = Cmin / Cmax

        NTU = UA / Cmin

        effectiveness = (
            1.0
            - math.exp(
                -NTU * (1 - Cr)
            )
        ) / (
            1.0
            - Cr
            * math.exp(
                -NTU * (1 - Cr)
            )
        )

        # ======================================================
        # DUTY
        # ======================================================

        q_max = (
            Cmin
            * (
                hot["t_k"]
                - cold["t_k"]
            )
        )

        q_actual = (
            effectiveness
            * q_max
        )

        # ======================================================
        # OUTLET TEMPERATURES
        # ======================================================

        th_out = (
            hot["t_k"]
            - q_actual / Ch
        )

        tc_out = (
            cold["t_k"]
            + q_actual / Cc
        )

        # ======================================================
        # PRESSURE DROP
        # ======================================================

        friction_factor_tube = float(self.specs.get("tube_friction_factor", 0.02))
        friction_factor_annulus = float(self.specs.get("annulus_friction_factor", 0.03))
        tube_dp = friction_factor_tube * (tube_length / max(tube_id, 1e-6)) * (cold["density"] * tube_velocity**2 / 2.0)
        annulus_dp = friction_factor_annulus * (tube_length / max(hydraulic_diameter, 1e-6)) * (hot["density"] * annulus_velocity**2 / 2.0)

        # ======================================================
        # DEBUG
        # ======================================================









        # ======================================================
        # RESULTS
        # ======================================================

        return {
            "hx_type": "double_pipe",
            "method": "basic",
            "Q": q_actual,
            "Area": area,
            "U_assumed": u_dirty,
            "U_calculated": u_dirty,
            "LMTD": None,
            "tube_count": parallel_paths,
            "parallel_paths": parallel_paths,
            "tube_od": tube_od,
            "tube_id": tube_id,
            "tube_length": tube_length,
            "shell_diameter": annulus_diameter,
            "tube_velocity": tube_velocity,
            "shell_velocity": annulus_velocity,
            "tube_dp": tube_dp,
            "shell_dp": annulus_dp,
            "iterations": 1,
            "status": "OK",
            "warnings": self._double_pipe_warnings(tube_velocity, annulus_velocity),
            "NTU": NTU,
            "effectiveness": effectiveness,
        }
