from __future__ import annotations

from typing import Any, Dict

from .base import HeatExchanger


class DoublePipeHX(HeatExchanger):
    def design(self) -> Dict[str, Any]:
        hot = self._stream_props(self.hot_in)
        cold = self._stream_props(self.cold_in)
        q = self.heat_duty(hot, cold)
        th_out = self.hot_out.temperature.to("K").value if self.hot_out and self.hot_out.temperature else hot["t_k"] - q / (hot["m_dot"] * hot["cp"])
        tc_out = self.cold_out.temperature.to("K").value if self.cold_out and self.cold_out.temperature else cold["t_k"] + q / (cold["m_dot"] * cold["cp"])
        lmtd = self.lmtd(hot["t_k"], th_out, cold["t_k"], tc_out)
        u = float(self.specs.get("U", 350.0).to("W/m2K").value)
        area = float(self.specs.get("area", self.area(q, u, lmtd)))
        return {
            "hx_type": "double_pipe",
            "Q": q,
            "Area": area,
            "U_assumed": u,
            "U_calculated": u,
            "LMTD": lmtd,
            "tube_count": 1,
            "shell_diameter": self.specs.get("annulus_diameter", 0.05),
            "tube_velocity": None,
            "shell_velocity": None,
            "tube_dp": self.specs.get("tube_dp", 0.0),
            "shell_dp": self.specs.get("shell_dp", 0.0),
            "iterations": 1,
            "status": "OK",
            "warnings": [],
        }
