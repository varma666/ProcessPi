from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from processpi.calculations.heat_transfer import HeatExchangerArea, LMTD, OverallHeatTransferCoefficient
from processpi.calculations.heat_transfer.heat_exchanger import SensibleHeatDuty


class HeatExchanger(ABC):
    """Base class for all heat exchanger equipment models."""

    def __init__(self, hot_fluid: Dict[str, Any], cold_fluid: Dict[str, Any], config: Dict[str, Any]):
        self.hot_fluid = hot_fluid or {}
        self.cold_fluid = cold_fluid or {}
        self.config = config or {}

    def heat_duty(self):
        if all(k in self.hot_fluid for k in ("mass_flow_rate", "specific_heat", "t_in", "t_out")):
            return SensibleHeatDuty(
                mass_flow_rate=self.hot_fluid["mass_flow_rate"],
                specific_heat=self.hot_fluid["specific_heat"],
                t_in=self.hot_fluid["t_in"],
                t_out=self.hot_fluid["t_out"],
            ).calculate()
        return SensibleHeatDuty(
            mass_flow_rate=self.cold_fluid["mass_flow_rate"],
            specific_heat=self.cold_fluid["specific_heat"],
            t_in=self.cold_fluid["t_out"],
            t_out=self.cold_fluid["t_in"],
        ).calculate()

    def lmtd(self):
        d_t1 = self.hot_fluid["t_in"] - self.cold_fluid["t_out"]
        d_t2 = self.hot_fluid["t_out"] - self.cold_fluid["t_in"]
        return LMTD(dT1=d_t1, dT2=d_t2).calculate()

    def overall_U(self):
        h_hot = self.config.get("h_hot", 500.0)
        h_cold = self.config.get("h_cold", 500.0)
        h_hot = getattr(h_hot, "value", h_hot)
        h_cold = getattr(h_cold, "value", h_cold)
        fouling_hot = self.config.get("fouling_hot", 0.0)
        fouling_cold = self.config.get("fouling_cold", 0.0)
        wall_resistance = self.config.get("wall_resistance", 0.0)
        resistances = [(1.0 / h_hot), wall_resistance, fouling_hot, fouling_cold, (1.0 / h_cold)]
        return OverallHeatTransferCoefficient(resistances=resistances).calculate()

    def area(self):
        return HeatExchangerArea(
            heat_duty=self.heat_duty(),
            overall_heat_transfer_coeff=self.overall_U(),
            log_mean_temp_diff=self.lmtd(),
        ).calculate()

    @abstractmethod
    def design(self) -> Dict[str, Any]:
        raise NotImplementedError
