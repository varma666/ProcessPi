from __future__ import annotations

import math
from typing import Any, Dict

from processpi.calculations.heat_transfer.hx_kern import (
    BoilingHTC,
    LatentDuty,
)

from .shell_and_tube import ShellAndTubeHX


class EvaporatorHX(ShellAndTubeHX):

    """
    Shell-and-tube evaporator.

    Architecture:
    - Reuses ShellAndTubeHX geometry engine
    - Reuses Bell/Kern framework
    - Reuses pressure-drop framework
    - Adds boiling-side heat transfer handling
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

        self.service_type = "evaporator"

    # ==========================================================
    # HEAT DUTY
    # ==========================================================

    def _calculate_heat_duty(
        self,
        hot: Dict[str, float],
        cold: Dict[str, float],
    ):

        latent_heat = self.specs.get(
            "latent_heat"
        )

        if latent_heat is None:

            raise ValueError(
                "Evaporator requires latent_heat."
            )

        # ======================================================
        # DUTY
        # ======================================================

        q_watts = (
            LatentDuty(
                m_dot=cold["m_dot"],
                latent_heat=latent_heat,
            )
            .calculate()
            .to("W")
            .value
        )

        q_max = (
            hot["m_dot"]
            * hot["cp"]
            * 1000.0
            * (
                hot["t_k"]
                - cold["t_k"]
            )
        )
        
        if q_watts > q_max:
        
            raise ValueError(
                "Evaporator duty exceeds "
                "available hot-side sensible heat."
            )

        # ======================================================
        # HOT SIDE COOLING
        # ======================================================

        th_in = hot["t_k"]

        th_out = (
            th_in
            - q_watts
            / max(
                hot["m_dot"]
                * hot["cp"]
                * 1000.0,
                1e-12,
            )
        )

        # ======================================================
        # BOILING SIDE
        # ======================================================

        tc_in = cold["t_k"]

        # boiling approx constant temperature
        tc_out = tc_in

        return (
            q_watts,
            th_out,
            tc_out,
        )

    # ==========================================================
    # BOILING HTC
    # ==========================================================

    def _calculate_boiling_htc(
        self,
        cold: Dict[str, float],
        geometry: Dict[str, float],
        q_flux: float,
    ) -> float:

        pressure = cold.get(
            "p_bar",
            1.0,
        )

        try:

            h_boil = (
                BoilingHTC(
                    heat_flux=q_flux,
                    pressure=pressure,
                )
                .calculate()
                .to("W/m2K")
                .value
            )

        except Exception:

            # fallback engineering estimate
            h_boil = 4000.0

        return max(h_boil, 1500.0)

    # ==========================================================
    # HTC CALCULATION
    # ==========================================================

    def _calculate_htc(
        self,
        dimless: Dict[str, float],
        geometry: Dict[str, float],
        hot: Dict[str, float],
        cold: Dict[str, float],
    ):

        # ======================================================
        # NORMAL SINGLE-PHASE SIDE
        # ======================================================

        h_tube, h_shell = super()._calculate_htc(
            dimless,
            geometry,
            hot,
            cold,
        )

        # ======================================================
        # HEAT FLUX
        # ======================================================

        area = max(
            geometry["area"],
            1e-9,
        )

        q_flux = (
            self.specs.get("Q", 1e6)
            / area
        )

        # ======================================================
        # BOILING SIDE HTC
        # ======================================================

        h_boil = self._calculate_boiling_htc(
            cold,
            geometry,
            q_flux,
        )

        # ======================================================
        # ASSUME COLD SIDE BOILING
        # ======================================================

        return (
            h_boil,
            h_shell,
        )

    # ==========================================================
    # DESIGN
    # ==========================================================

    def design(self):

        results = super().design()

        results["hx_type"] = "evaporator"

        results["service"] = "evaporator"

        results["phase_change"] = True

        return results

    # ==========================================================
    # RATE
    # ==========================================================

    def rate(self):

        results = super().rate()

        results["hx_type"] = "evaporator"

        results["service"] = "evaporator"

        results["phase_change"] = True

        return results
