from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from processpi.calculations.heat_transfer import HeatExchangerArea, LMTD, OverallHeatTransferCoefficient
from processpi.calculations.heat_transfer.hx_kern import LatentDuty, SensibleDuty
from processpi.streams.material import MaterialStream


class HeatExchanger(ABC):
    def __init__(self, hot_in: MaterialStream, cold_in: MaterialStream, hot_out: Optional[MaterialStream] = None, cold_out: Optional[MaterialStream] = None, **specs: Any):
        self.hot_in = hot_in
        self.cold_in = cold_in
        self.hot_out = hot_out
        self.cold_out = cold_out
        self.specs = specs

    def _stream_props(self, s: MaterialStream) -> Dict[str, float]:
        return {
            "density": s.density.to("kg/m3").value,
            "viscosity": s.component.viscosity().to("Pa·s").value if s.component and hasattr(s.component, "viscosity") else self.specs.get("viscosity", 1e-3),
            "cp": s.specific_heat.to("J/kgK").value if s.specific_heat else self.specs.get("cp", 4180.0),
            "k": s.component.thermal_conductivity().to("W/mK").value if s.component and hasattr(s.component, "thermal_conductivity") else self.specs.get("thermal_conductivity", 0.6),
            "m_dot": s.mass_flow().to("kg/s").value if s.mass_flow() else self.specs.get("mass_flow_rate", 1.0),
            "p_bar": s.pressure.to("bar").value if s.pressure else 1.0,
            "phase": (s.phase or "liquid").lower(),
            "t_k": s.temperature.to("K").value if s.temperature else None,
        }

    def heat_duty(self, hot: Dict[str, float], cold: Dict[str, float]) -> float:
        if self.specs.get("Q") is not None:
            return float(self.specs["Q"])
        if self.specs.get("latent_heat") is not None:
            return LatentDuty(m_dot=hot["m_dot"], latent_heat=self.specs["latent_heat"]).calculate().to("W").value
        if self.hot_out and hot["t_k"] is not None and self.hot_out.temperature is not None:
            return SensibleDuty(m_dot=hot["m_dot"], cp=hot["cp"], t_in=hot["t_k"], t_out=self.hot_out.temperature.to("K").value).calculate().to("W").value
        if self.cold_out and cold["t_k"] is not None and self.cold_out.temperature is not None:
            return SensibleDuty(m_dot=cold["m_dot"], cp=cold["cp"], t_in=self.cold_out.temperature.to("K").value, t_out=cold["t_k"]).calculate().to("W").value
        raise ValueError("Insufficient thermal specification. Provide one outlet stream or Q/latent_heat.")

    def lmtd(self, th_in: float, th_out: float, tc_in: float, tc_out: float) -> float:
        return LMTD(dT1=th_in - tc_out, dT2=th_out - tc_in).calculate()

    def area(self, q_w: float, u: float, dtlm: float) -> float:
        return HeatExchangerArea(heat_duty=q_w, overall_heat_transfer_coeff=u, log_mean_temp_diff=dtlm).calculate().to("m2").value

    def overall_u(self, h_tube: float, h_shell: float, fouling_factor: float = 0.0) -> float:
        u = OverallHeatTransferCoefficient(resistances=[1.0 / h_tube, fouling_factor, 1.0 / h_shell]).calculate()
        return u.to("W/m2K").value

    @abstractmethod
    def design(self) -> Dict[str, Any]:
        raise NotImplementedError
