from __future__ import annotations

import math

from typing import Any, Dict

from .base import HeatExchanger


class DoublePipeHX(HeatExchanger):

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
            self.hot_out.temperature.to("K").value
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
            self.cold_out.temperature.to("K").value
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

        u_assumed = float(
            self.specs.get(
                "U",
                350.0,
            ).to("W/m2K").value
        )

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

        tube_velocity = (
            cold["m_dot"]
            / (
                cold["density"]
                * tube_area
            )
        )

        annulus_velocity = (
            hot["m_dot"]
            / (
                hot["density"]
                * annulus_area
            )
        )

        # ======================================================
        # PRESSURE DROP
        # ======================================================

        tube_dp = (
            0.5
            * cold["density"]
            * tube_velocity**2
        )

        annulus_dp = (
            0.5
            * hot["density"]
            * annulus_velocity**2
        )

        # ======================================================
        # DEBUG
        # ======================================================

        print("\n" + "=" * 60)
        print("DOUBLE PIPE HX — DESIGN MODE")
        print("=" * 60)

        print(f"Heat Duty          : {q:.4f} kW")
        print(f"LMTD               : {lmtd:.4f} K")
        print(f"U Assumed          : {u_assumed:.4f} W/m2.K")
        print(f"Required Area      : {area_required:.4f} m2")
        print(f"Actual Area        : {area:.4f} m2")

        print("-" * 60)

        print(f"Tube Velocity      : {tube_velocity:.4f} m/s")
        print(f"Annulus Velocity   : {annulus_velocity:.4f} m/s")

        print("-" * 60)

        print(f"Tube DP            : {tube_dp:.2f} Pa")
        print(f"Annulus DP         : {annulus_dp:.2f} Pa")

        print("=" * 60)

        # ======================================================
        # RESULTS
        # ======================================================

        return {
            "hx_type": "double_pipe",
            "method": "basic",
            "Q": q,
            "Area": area,
            "U_assumed": u_assumed,
            "U_calculated": u_assumed,
            "LMTD": lmtd,
            "tube_count": 1,
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
            "warnings": [],
        }

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

        tube_velocity = (
            cold["m_dot"]
            / (
                cold["density"]
                * tube_area
            )
        )

        annulus_velocity = (
            hot["m_dot"]
            / (
                hot["density"]
                * annulus_area
            )
        )

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

        tube_dp = (
            0.5
            * cold["density"]
            * tube_velocity**2
        )

        annulus_dp = (
            0.5
            * hot["density"]
            * annulus_velocity**2
        )

        # ======================================================
        # DEBUG
        # ======================================================

        print("\n" + "=" * 60)
        print("DOUBLE PIPE HX — RATE MODE")
        print("=" * 60)

        print(f"UA                 : {UA:.4f}")
        print(f"NTU                : {NTU:.4f}")
        print(f"Effectiveness      : {effectiveness:.4f}")

        print("-" * 60)

        print(f"Actual Duty        : {q_actual/1000:.4f} kW")

        print(f"Hot Outlet Temp    : {th_out:.2f} K")
        print(f"Cold Outlet Temp   : {tc_out:.2f} K")

        print("-" * 60)

        print(f"Tube Velocity      : {tube_velocity:.4f} m/s")
        print(f"Annulus Velocity   : {annulus_velocity:.4f} m/s")

        print("=" * 60)

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
            "tube_count": 1,
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
            "warnings": [],
            "NTU": NTU,
            "effectiveness": effectiveness,
        }
