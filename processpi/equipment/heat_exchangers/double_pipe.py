from __future__ import annotations

from typing import Any, Dict

from processpi.calculations.fluids import FluidVelocity
from processpi.calculations.heat_transfer.heat_exchanger import (
    ConvectiveCoefficient,
    DarcyPressureDrop,
    KernNusselt,
    ReynoldsFromProperties,
)

from .base import HeatExchanger


class DoublePipeHX(HeatExchanger):
    def design(self) -> Dict[str, Any]:
        inner_d = self.config.get("inner_diameter", 0.025)
        annulus_d = self.config.get("annulus_hydraulic_diameter", 0.04)
        length = self.config.get("length", 6.0)

        v_inner = FluidVelocity(volumetric_flow_rate=self.hot_fluid["mass_flow_rate"] / self.hot_fluid["density"], diameter=inner_d).calculate()
        v_annulus = FluidVelocity(volumetric_flow_rate=self.cold_fluid["mass_flow_rate"] / self.cold_fluid["density"], diameter=annulus_d).calculate()

        re_inner = ReynoldsFromProperties(density=self.hot_fluid["density"], velocity=v_inner, diameter=inner_d, viscosity=self.hot_fluid["viscosity"]).calculate()
        re_annulus = ReynoldsFromProperties(density=self.cold_fluid["density"], velocity=v_annulus, diameter=annulus_d, viscosity=self.cold_fluid["viscosity"]).calculate()

        nu_inner = KernNusselt(reynolds=re_inner, prandtl=self.hot_fluid.get("prandtl", 4.0), n=0.4).calculate()
        nu_annulus = KernNusselt(reynolds=re_annulus, prandtl=self.cold_fluid.get("prandtl", 4.0), n=0.3).calculate()

        self.config["h_hot"] = ConvectiveCoefficient(nusselt=nu_inner, thermal_conductivity=self.hot_fluid["thermal_conductivity"], characteristic_diameter=inner_d).calculate()
        self.config["h_cold"] = ConvectiveCoefficient(nusselt=nu_annulus, thermal_conductivity=self.cold_fluid["thermal_conductivity"], characteristic_diameter=annulus_d).calculate()

        return {
            "hx_type": "double_pipe",
            "duty_W": self.heat_duty(),
            "lmtd_K": self.lmtd(),
            "overall_U_W_m2K": self.overall_U(),
            "required_area_m2": self.area(),
            "inner_dp_Pa": DarcyPressureDrop(friction_factor=self.config.get("f_inner", 0.01), length=length, diameter=inner_d, density=self.hot_fluid["density"], velocity=v_inner).calculate(),
            "annulus_dp_Pa": DarcyPressureDrop(friction_factor=self.config.get("f_annulus", 0.02), length=length, diameter=annulus_d, density=self.cold_fluid["density"], velocity=v_annulus).calculate(),
        }
