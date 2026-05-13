from __future__ import annotations

import math
from typing import Any, Dict

from processpi.calculations.heat_transfer.hx_kern import (
    CondensationHTC,
    LatentDuty,
)

from .shell_and_tube import ShellAndTubeHX


class CondenserHX(ShellAndTubeHX):

    """
    Shell-and-tube condenser.

    Architecture:
    - Reuses ShellAndTubeHX geometry engine
    - Reuses pressure-drop framework
    - Reuses Bell/Kern infrastructure
    - Adds condensation heat transfer handling
    """

    def __init__(
        self,
        *args: Any,
        method: str = "kern",
        **kwargs: Any,
    ):

        super().__init__(
            *args,
            method=method,
            **kwargs,
        )

        self.service_type = "condenser"

    # ==========================================================
    # OVERRIDE DUTY
    # ==========================================================

    def _calculate_heat_duty(
        self,
        hot: Dict[str, float],
        cold: Dict[str, float],
    ):

        latent_heat = self.specs.get("latent_heat")

        if latent_heat is None:

            raise ValueError(
                "Condenser requires latent_heat "
                "for vapor condensation."
            )

        q_watts = (
            LatentDuty(
                m_dot=hot["m_dot"],
                latent_heat=latent_heat,
            )
            .calculate()
            .to("W")
            .value
        )

        th_in = hot["t_k"]

        # Condensing vapor assumed nearly constant temperature
        th_out = th_in

        tc_in = cold["t_k"]

        tc_out = (
            tc_in
            + q_watts
            / max(
                cold["m_dot"] * cold["cp"] * 1000.0,
                1e-12,
            )
        )

        return (
            q_watts,
            th_out,
            tc_out,
        )

    # ==========================================================
    # CONDENSATION HTC
    # ==========================================================

    def _calculate_condensation_htc(
        self,
        hot: Dict[str, float],
        geometry: Dict[str, float],
    ) -> float:

        vapor_density = hot.get("density", 1.0)

        liquid_density = self.specs.get(
            "condensate_density",
            vapor_density * 50.0,
        )

        liquid_viscosity = self.specs.get(
            "condensate_viscosity",
            0.0003,
        )

        liquid_k = self.specs.get(
            "condensate_k",
            0.1,
        )

        latent_heat = self.specs.get(
            "latent_heat",
        )

        delta_t = max(
            self.specs.get("condensation_dT", 5.0),
            1e-6,
        )

        tube_length = geometry["tube_length"]

        try:

            h_cond = (
                CondensationHTC(
                    rho_l=liquid_density,
                    rho_v=vapor_density,
                    mu_l=liquid_viscosity,
                    k_l=liquid_k,
                    h_fg=latent_heat,
                    delta_t=delta_t,
                    length=tube_length,
                )
                .calculate()
                .to("W/m2K")
                .value
            )

        except Exception:

            # fallback realistic range
            h_cond = 5000.0

        return max(h_cond, 1000.0)

    # ==========================================================
    # OVERRIDE HTC CALCULATION
    # ==========================================================

    def _calculate_htc(
        self,
        dimless: Dict[str, float],
        geometry: Dict[str, float],
        hot: Dict[str, float],
        cold: Dict[str, float],
    ):

        # ======================================================
        # HOT SIDE = CONDENSING VAPOR
        # ======================================================

        h_cond = self._calculate_condensation_htc(
            hot,
            geometry,
        )

        # ======================================================
        # COLD SIDE = NORMAL COOLING FLUID
        # ======================================================

        _, h_shell = super()._calculate_htc(
            dimless,
            geometry,
            hot,
            cold,
        )

        return (
            h_cond,
            h_shell,
        )

    # ==========================================================
    # DESIGN
    # ==========================================================

    def design(self):

        results = super().design()

        results["hx_type"] = "condenser"

        results["service"] = "total_condenser"

        results["phase_change"] = True

        return results

    # ==========================================================
    # RATE
    # ==========================================================

    def rate(self):

        results = super().rate()

        results["hx_type"] = "condenser"

        results["service"] = "total_condenser"

        results["phase_change"] = True

        return results
