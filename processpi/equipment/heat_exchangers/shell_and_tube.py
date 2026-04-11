from __future__ import annotations

import math
from typing import Any, Dict

from processpi.calculations.fluids import FluidVelocity
from processpi.calculations.heat_transfer.heat_exchanger import (
    ConvectiveCoefficient,
    DarcyPressureDrop,
    KernNusselt,
    ReynoldsFromProperties,
)

from .base import HeatExchanger


class ShellAndTubeHX(HeatExchanger):
    """Shell-and-tube exchanger design using a simplified Kern-style workflow."""

    def design(self) -> Dict[str, Any]:
        tube_diameter = self.config.get("tube_inner_diameter", 0.019)
        shell_equiv_diameter = self.config.get("shell_equiv_diameter", 0.05)
        tube_count = self.config.get("tube_count", 100)
        tube_passes = self.config.get("tube_passes", 2)
        tube_length = self.config.get("tube_length", 5.0)

        tube_flow_area = max(math.pi * tube_diameter**2 / 4.0 * (tube_count / max(tube_passes, 1)), 1e-12)
        shell_flow_area = max(self.config.get("shell_flow_area", 0.25 * math.pi * shell_equiv_diameter**2), 1e-12)

        q_hot = self.hot_fluid["mass_flow_rate"] / max(self.hot_fluid["density"], 1e-12)
        q_cold = self.cold_fluid["mass_flow_rate"] / max(self.cold_fluid["density"], 1e-12)

        v_tube = FluidVelocity(volumetric_flow_rate=q_hot, diameter=(4 * tube_flow_area / math.pi) ** 0.5).calculate()
        v_shell = FluidVelocity(volumetric_flow_rate=q_cold, diameter=(4 * shell_flow_area / math.pi) ** 0.5).calculate()

        re_tube = ReynoldsFromProperties(
            density=self.hot_fluid["density"], velocity=v_tube, diameter=tube_diameter, viscosity=self.hot_fluid["viscosity"]
        ).calculate()
        re_shell = ReynoldsFromProperties(
            density=self.cold_fluid["density"], velocity=v_shell, diameter=shell_equiv_diameter, viscosity=self.cold_fluid["viscosity"]
        ).calculate()

        nu_tube = KernNusselt(reynolds=re_tube, prandtl=self.hot_fluid.get("prandtl", 4.0), n=0.4).calculate()
        nu_shell = KernNusselt(reynolds=re_shell, prandtl=self.cold_fluid.get("prandtl", 4.0), n=0.3).calculate()

        h_hot = ConvectiveCoefficient(
            nusselt=nu_tube,
            thermal_conductivity=self.hot_fluid["thermal_conductivity"],
            characteristic_diameter=tube_diameter,
        ).calculate()
        h_cold = ConvectiveCoefficient(
            nusselt=nu_shell,
            thermal_conductivity=self.cold_fluid["thermal_conductivity"],
            characteristic_diameter=shell_equiv_diameter,
        ).calculate()

        self.config["h_hot"] = h_hot
        self.config["h_cold"] = h_cold

        duty = self.heat_duty()
        lmtd = self.lmtd()
        overall_u = self.overall_U()
        area = self.area()

        f_tube = self.config.get("f_tube", 0.005)
        f_shell = self.config.get("f_shell", 0.02)

        dp_tube = DarcyPressureDrop(
            friction_factor=f_tube,
            length=tube_length * tube_passes,
            diameter=tube_diameter,
            density=self.hot_fluid["density"],
            velocity=v_tube,
        ).calculate()
        dp_shell = DarcyPressureDrop(
            friction_factor=f_shell,
            length=tube_length,
            diameter=shell_equiv_diameter,
            density=self.cold_fluid["density"],
            velocity=v_shell,
        ).calculate()

        return {
            "hx_type": "shell_and_tube",
            "duty_W": duty,
            "lmtd_K": lmtd,
            "overall_U_W_m2K": overall_u,
            "required_area_m2": area,
            "tube_side": {"velocity_m_s": v_tube, "reynolds": re_tube, "h_W_m2K": h_hot, "dp_Pa": dp_tube},
            "shell_side": {"velocity_m_s": v_shell, "reynolds": re_shell, "h_W_m2K": h_cold, "dp_Pa": dp_shell},
        }
