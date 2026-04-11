from __future__ import annotations

from typing import Dict

from processpi.calculations.heat_transfer.heat_exchanger import LatentHeatDuty

from .base import HeatExchanger


class CondenserHX(HeatExchanger):
    def design(self) -> Dict[str, object]:
        duty = LatentHeatDuty(
            mass_flow_rate=self.hot_fluid["mass_flow_rate"],
            latent_heat=self.hot_fluid["latent_heat"],
        ).calculate()
        return {
            "hx_type": "condenser",
            "duty_W": duty,
            "lmtd_K": self.lmtd(),
            "overall_U_W_m2K": self.overall_U(),
            "required_area_m2": self.area(),
        }
