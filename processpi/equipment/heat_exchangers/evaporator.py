from __future__ import annotations

from typing import Dict

from processpi.calculations.heat_transfer.heat_exchanger import LatentHeatDuty

from .base import HeatExchanger


class EvaporatorHX(HeatExchanger):
    def design(self) -> Dict[str, object]:
        duty = LatentHeatDuty(
            mass_flow_rate=self.cold_fluid["mass_flow_rate"],
            latent_heat=self.cold_fluid["latent_heat"],
        ).calculate()
        return {
            "hx_type": "evaporator",
            "duty_W": duty,
            "lmtd_K": self.lmtd(),
            "overall_U_W_m2K": self.overall_U(),
            "required_area_m2": self.area(),
        }
