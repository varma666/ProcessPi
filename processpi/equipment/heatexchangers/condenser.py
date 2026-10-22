
from __future__ import annotations

from typing import Any, Dict

from processpi.calculations.heat_transfer.hx_kern import (
    CondensationHTC,
    LatentDuty,
)

from .shell_and_tube import ShellAndTubeHX


class CondenserHX(ShellAndTubeHX):
    """Shell-and-tube condenser with phase-change and unit safeguards.

    Latent-heat convention:
        * Unit-aware values are converted to J/kg.
        * Bare numeric values are interpreted as J/kg.
    """

    _PHASE_CHANGE_SERVICE = "condenser"

    def __init__(self, *args: Any, method: str = "kern", **kwargs: Any):
        super().__init__(*args, method=method, **kwargs)

        self.service_type = "condenser"
        self.orientation = str(
            self.specs.get("orientation", "horizontal")
        ).lower()
        self.condensing_side = str(
            self.specs.get("condensing_side", "shell")
        ).lower()

        if self.orientation not in {"horizontal", "vertical"}:
            raise ValueError(
                "orientation must be 'horizontal' or 'vertical', "
                f"got {self.orientation!r}"
            )

        if self.condensing_side not in {"shell", "tube"}:
            raise ValueError(
                "condensing_side must be 'shell' or 'tube', "
                f"got {self.condensing_side!r}"
            )

        # Keep the condensing stream on the requested side.
        self._FIXED_TUBE_SIDE = (
            "hot" if self.condensing_side == "tube" else "cold"
        )

        self.condensation_mode = str(
            self.specs.get("condensation_mode", "total")
        ).lower()

        if self.condensation_mode not in {"total", "partial"}:
            raise ValueError(
                "condensation_mode must be 'total' or 'partial', "
                f"got {self.condensation_mode!r}"
            )

    def _latent_heat_j_kg(self) -> float:
        """Return configured latent heat in J/kg.

        Unit-aware values must support .to('J/kg'). Numeric values
        are interpreted as J/kg; no implicit kJ/kg conversion is made.
        """
        latent_heat = self.specs.get("latent_heat")

        # Match the phase-change energy-balance resolver: when the caller
        # omits an explicit value, use the condensing component's latent heat
        # (or enthalpy alias) when available.
        if latent_heat is None:
            latent_heat = self._latent_heat_for_energy_balance()

        if latent_heat is None:
            raise ValueError(
                "Condenser requires latent_heat in J/kg, a component with "
                "latent-heat data, or a unit-aware latent-heat quantity."
            )

        if hasattr(latent_heat, "to") and callable(latent_heat.to):
            latent_heat_j_kg = self._safe_float(
                latent_heat.to("J/kg"), "latent_heat"
            )
        else:
            try:
                latent_heat_j_kg = float(latent_heat)
            except (TypeError, ValueError) as exc:
                raise TypeError(
                    "latent_heat must be numeric in J/kg or "
                    "a unit-aware quantity convertible to J/kg."
                ) from exc

        # A missing component property can evaluate to a tiny positive
        # floating-point residue (for example ~1e-35 J/kg). Treat that as
        # unavailable data rather than producing a near-zero condenser duty
        # that appears thermally feasible.
        if not latent_heat_j_kg > 1.0:
            raise ValueError(
                "latent_heat is unavailable or physically negligible: "
                f"got {latent_heat_j_kg!r} J/kg. Supply a valid latent_heat "
                "in J/kg or provide component latent-heat data."
            )

        return latent_heat_j_kg

    def _calculate_heat_duty(
        self,
        hot: Dict[str, float],
        cold: Dict[str, float],
        **kwargs: Any,
    ):
        """Calculate latent duty and the corresponding coolant outlet.

        Returns:
            (heat_duty_W, hot_outlet_temperature_K,
             cold_outlet_temperature_K)
        """
        latent_heat_j_kg = self._latent_heat_j_kg()

        default_fraction = (
            1.0 if self.condensation_mode == "total" else 0.5
        )
        vapor_fraction = float(
            self.specs.get("vapor_fraction_condensed", default_fraction)
        )

        if not 0.0 < vapor_fraction <= 1.0:
            raise ValueError(
                "vapor_fraction_condensed must be greater than 0 "
                "and no greater than 1."
            )

        m_dot_hot = float(hot["m_dot"])
        m_dot_cold = float(cold["m_dot"])
        cp_cold = float(cold["cp"])

        if m_dot_hot <= 0.0:
            raise ValueError("Hot-side mass flow must be positive.")

        if m_dot_cold <= 0.0 or cp_cold <= 0.0:
            raise ValueError(
                "Cold-side mass flow and specific heat must be positive."
            )

        q_watts = self._safe_float(
            LatentDuty(
                m_dot=m_dot_hot * vapor_fraction,
                latent_heat=latent_heat_j_kg,
            ).calculate().to("W"),
            "q_watts",
        )

        th_in = float(hot["t_k"])
        tc_in = float(cold["t_k"])

        subcooling = float(self.specs.get("subcooling", 0.0))
        if subcooling < 0.0:
            raise ValueError("subcooling cannot be negative.")

        # Approximate condensing temperature as constant. Subcooling
        # is applied to the hot outlet temperature.
        th_out = th_in - subcooling
        tc_out = tc_in + q_watts / (m_dot_cold * cp_cold)

        # Do not silently clip the coolant temperature and leave the
        # duty inconsistent with the energy balance.
        minimum_approach = float(
            self.specs.get("minimum_approach_temperature", 1.0)
        )
        if minimum_approach <= 0.0:
            raise ValueError(
                "minimum_approach_temperature must be positive."
            )

        if tc_out >= th_in - minimum_approach:
            raise ValueError(
                "Condenser energy balance is thermally infeasible: "
                f"calculated cold outlet is {tc_out:.3f} K, while the "
                f"maximum allowed outlet for the specified approach is "
                f"{th_in - minimum_approach:.3f} K. Check latent_heat, "
                "vapor_fraction_condensed, flow rates and inlet temperatures."
            )

        return q_watts, th_out, tc_out

    def _calculate_ft(self, *args: Any, **kwargs: Any) -> float:
        """Use Ft = 1 for the current idealized phase-change model."""
        return 1.0

    def _calculate_condensation_htc(
        self,
        hot: Dict[str, float],
        geometry: Dict[str, float],
    ) -> float:
        """Estimate condensation-side heat-transfer coefficient."""
        vapor_density = max(float(hot.get("density", 1.0)), 0.1)

        liquid_density = max(
            float(
                self.specs.get(
                    "condensate_density", vapor_density * 50.0
                )
            ),
            vapor_density + 1.0,
        )
        liquid_viscosity = max(
            float(self.specs.get("condensate_viscosity", 3e-4)),
            1e-5,
        )
        liquid_k = max(
            float(self.specs.get("condensate_k", 0.1)),
            0.01,
        )

        latent_heat_j_kg = self._latent_heat_j_kg()
        delta_t = max(
            float(self.specs.get("condensation_dT", 5.0)),
            0.5,
        )
        length = max(
            float(geometry.get("tube_length", 6.0)),
            0.5,
        )

        h_base = self._safe_float(
            CondensationHTC(
                rho_l=liquid_density,
                rho_v=vapor_density,
                mu_l=liquid_viscosity,
                k_l=liquid_k,
                h_fg=latent_heat_j_kg,
                delta_t=delta_t,
                length=length,
            ).calculate().to("W/m2K"),
            "h_base",
        )

        orientation_factor = (
            1.0 if self.orientation == "vertical" else 0.85
        )
        side_factor = 0.9 if self.condensing_side == "tube" else 1.0

        h_cond = h_base * orientation_factor * side_factor

        # Retain the existing numerical bounds. These bounds are
        # safeguards, not a substitute for validating the HTC model.
        return max(1200.0, min(h_cond, 20000.0))

    def _get_velocity_limits(
        self,
        side: str,
        component,
    ) -> tuple[float, float]:
        """Use phase-change velocity limits on the condensing side."""
        if side == self.condensing_side:
            return self._phase_velocity_limits(side, component)

        return super()._get_velocity_limits(side, component)

    def _shell_side_is_single_phase(self) -> bool:
        """Return whether the shell side is treated as single phase."""
        return self.condensing_side != "shell"

    def _calculate_htc(
        self,
        dimless: Dict[str, float],
        geometry: Dict[str, float],
        tube: Dict[str, float],
        shell: Dict[str, float],
        **kwargs: Any,
    ):
        """Replace the HTC on the configured condensing side."""
        h_tube, h_shell = super()._calculate_htc(
            dimless, geometry, tube, shell
        )

        hot, _ = self._hot_cold_props(tube, shell)
        h_cond = self._calculate_condensation_htc(hot, geometry)

        if self.condensing_side == "tube":
            h_tube = h_cond
        else:
            h_shell = h_cond

        return h_tube, h_shell

    def _calculate_pressure_drop(
        self,
        geometry: Dict[str, float],
        tube: Dict[str, float],
        shell: Dict[str, float],
        shell_velocity: float | None = None,
        tube_velocity: float | None = None,
        **kwargs: Any,
    ):
        """Calculate side pressure drops, including vertical static head."""
        if shell_velocity is None:
            shell_velocity = float(
                kwargs.get("shell_velocity", kwargs.get("v_shell", 0.0))
            )

        if tube_velocity is None:
            tube_velocity = float(
                kwargs.get("tube_velocity", kwargs.get("v_tube", 0.0))
            )

        shell_passes = int(kwargs.get("shell_passes", 1))
        tube_passes = int(kwargs.get("tube_passes", 1))

        # Preserve the geometric inputs required by the base pressure-drop
        # calculation, particularly shell diameter and baffle spacing.
        passthrough = {
            key: kwargs[key]
            for key in (
                "shell_diameter",
                "baffle_spacing",
                "tube_length",
                "tube_id",
            )
            if key in kwargs
        }

        tube_dp, shell_dp = super()._calculate_pressure_drop(
            geometry=geometry,
            tube=tube,
            shell=shell,
            shell_velocity=shell_velocity,
            tube_velocity=tube_velocity,
            shell_passes=shell_passes,
            tube_passes=tube_passes,
            **passthrough,
        )

        orientation = str(
            kwargs.get("orientation", self.orientation)
        ).lower()

        if orientation == "vertical":
            condensate_density = float(
                self.specs.get("condensate_density", 850.0)
            )
            tube_length = max(
                float(geometry.get("tube_length", 6.0)),
                0.0,
            )
            static_head = condensate_density * 9.81 * tube_length

            if self.condensing_side == "tube":
                tube_dp += static_head
            else:
                shell_dp += static_head

        return tube_dp, shell_dp

    def _decorate_results(
        self,
        results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add condenser-specific metadata and de-duplicate warnings."""
        results.update(
            {
                "hx_type": "condenser",
                "service": self.condensation_mode + "_condenser",
                "phase_change": True,
                "orientation": self.orientation,
                "condensing_side": self.condensing_side,
                "convergence_status": results.get("status", "OK"),
                "warnings": list(
                    dict.fromkeys(
                        [*results.get("warnings", []), *self._warnings]
                    )
                ),
            }
        )
        return results

    def design(self):
        return self._decorate_results(super().design())

    def rate(self):
        return self._decorate_results(super().rate())
