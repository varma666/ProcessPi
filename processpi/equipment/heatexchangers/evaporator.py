from __future__ import annotations

from typing import Any, Dict

from processpi.calculations.heat_transfer.hx_kern import (
    BoilingHTC,
    LatentDuty,
)

from .shell_and_tube import ShellAndTubeHX


class EvaporatorHX(ShellAndTubeHX):
    """
    Shell-and-tube evaporator / reboiler thermal model.

    Design principles
    -----------------
    1. Required phase-change duty is calculated from the actual
       boiling-side mass flow.
    2. Mass flow may originate from either inlet or outlet stream.
    3. Required duty is NEVER clipped to available heating-side duty.
    4. Heating-side capacity is checked independently.
    5. Thermal infeasibility is reported explicitly.
    6. User-specified hot outlet temperature is used for the
       design temperature driving force when the requested duty
       exceeds available heating capacity.
    """

    # Evaporator/reboiler configuration historically keeps the heating
    # stream in the tubes and the boiling stream on the shell.
    _FIXED_TUBE_SIDE = "hot"

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

        self.orientation = str(
            self.specs.get(
                "orientation",
                "horizontal",
            )
        ).lower()

        self.boiling_side = str(
            self.specs.get(
                "boiling_side",
                "shell",
            )
        ).lower()

        if self.boiling_side not in {"tube", "shell"}:
            raise ValueError(
                "boiling_side must be 'tube' or 'shell'"
            )

        self.design_limits = {
            "max_shell_diameter": float(
                self.specs.get(
                    "max_shell_diameter",
                    2.0,
                )
            ),

            "max_tube_count": int(
                self.specs.get(
                    "max_tube_count",
                    5000,
                )
            ),

            "min_tube_velocity": float(
                self.specs.get(
                    "min_tube_velocity",
                    0.3,
                )
            ),

            "max_tube_velocity": float(
                self.specs.get(
                    "max_tube_velocity",
                    2.5,
                )
            ),

            "min_shell_velocity": float(
                self.specs.get(
                    "min_shell_velocity",
                    0.2,
                )
            ),

            "target_tube_velocity": float(
                self.specs.get(
                    "target_tube_velocity",
                    1.0,
                )
            ),

            "target_shell_velocity": float(
                self.specs.get(
                    "target_shell_velocity",
                    0.5,
                )
            ),

            "max_area": float(
                self.specs.get(
                    "max_area",
                    1000.0,
                )
            ),
        }

        # Thermal bookkeeping
        self._thermal_duty_required = None
        self._thermal_duty_available = None
        self._thermal_duty_deficit = None
        self._thermal_feasible = True
        self._thermal_duty_source = None

    # ==============================================================
    # OUTLET TEMPERATURE HELPER
    # ==============================================================

    def _explicit_outlet_temperature(
        self,
        stream,
    ) -> float | None:
        """
        Return user-specified outlet temperature in K.

        MaterialStream may inherit its component's default temperature.
        That inherited value is not treated as an explicit outlet target.
        """

        if stream is None:
            return None

        temperature = getattr(
            stream,
            "temperature",
            None,
        )

        if temperature is None:
            return None

        component = getattr(
            stream,
            "component",
            None,
        )

        component_temperature = getattr(
            component,
            "temperature",
            None,
        )

        if (
            component_temperature is not None
            and temperature is component_temperature
        ):
            return None

        return self._safe_float(
            temperature.to("K"),
            "outlet_temperature",
        )

    # ==============================================================
    # HEAT DUTY
    # ==============================================================

    def _calculate_heat_duty(
        self,
        hot: Dict[str, float],
        cold: Dict[str, float],
        **kwargs: Any,
    ):
        """
        Calculate required phase-change duty.

        Required duty:

            Q_required = m_boiling * latent_heat

        Heating-side available duty is calculated independently.

        IMPORTANT:
            Q_required is never clipped to Q_available.
        """

        latent_heat = (
            self.specs.get("latent_heat")
            or self._resolve_phase_change_latent_heat(
                hot,
                cold,
            )
        )

        if latent_heat is None:
            raise ValueError(
                "Evaporator/reboiler requires latent_heat "
                "or detectable phase-change service."
            )

        if hasattr(latent_heat, "to"):
            latent_heat_jkg = self._safe_float(
                latent_heat.to("J/kg"),
                "latent_heat",
            )
        else:
            latent_heat_jkg = self._safe_float(
                latent_heat,
                "latent_heat",
            )

        if latent_heat_jkg <= 0:
            raise ValueError(
                "latent_heat must be greater than zero."
            )

        # ----------------------------------------------------------
        # Identify actual boiling side
        # ----------------------------------------------------------

        if self.boiling_side == "tube":
            boiling = hot
        else:
            boiling = cold

        # ----------------------------------------------------------
        # Required latent duty
        # ----------------------------------------------------------

        q_required = self._safe_float(
            LatentDuty(
                m_dot=boiling["m_dot"],
                latent_heat=latent_heat_jkg,
            )
            .calculate()
            .to("W"),
            "q_required",
        )

        if q_required <= 0:
            raise ValueError(
                "Calculated phase-change duty must be positive."
            )

        self._thermal_duty_required = q_required

        self._thermal_duty_source = (
            boiling.get(
                "m_dot_source",
                "stream",
            )
        )

        # ----------------------------------------------------------
        # Heating side
        # ----------------------------------------------------------

        heating = (
            cold
            if self.boiling_side == "tube"
            else hot
        )

        heating_in = heating["t_k"]
        boiling_temperature = boiling["t_k"]

        # ----------------------------------------------------------
        # User-specified heating outlet
        # ----------------------------------------------------------

        if self.boiling_side == "tube":
            # Cold side is the heating side when the boiling fluid
            # is assigned to the tubes.
            explicit_heating_out = (
                self._explicit_outlet_temperature(
                    self.cold_out
                )
            )
        else:
            # Hot side is the heating side when the boiling fluid
            # is assigned to the shell.
            explicit_heating_out = (
                self._explicit_outlet_temperature(
                    self.hot_out
                )
            )
        # ----------------------------------------------------------
        # Available heating-side duty
        # ----------------------------------------------------------

        if explicit_heating_out is not None:
            heating_delta_t = max(
                heating_in - explicit_heating_out,
                0.0,
            )

            q_available = (
                heating["m_dot"]
                * heating["cp"]
                * heating_delta_t
            )

            available_basis = (
                f"specified heating outlet "
                f"{explicit_heating_out:.2f} K"
            )

        else:
            # No outlet temperature supplied.
            #
            # For sensible heating/cooling, do not allow the heating
            # fluid to cross the boiling temperature. A small approach
            # is retained for numerical stability.
            minimum_approach = float(
                self.specs.get(
                    "minimum_phase_change_approach",
                    0.5,
                )
            )

            maximum_useful_outlet = (
                boiling_temperature
                + minimum_approach
            )

            heating_delta_t = max(
                heating_in - maximum_useful_outlet,
                0.0,
            )

            q_available = (
                heating["m_dot"]
                * heating["cp"]
                * heating_delta_t
            )

            available_basis = (
                "maximum sensible heating capacity "
                f"with {minimum_approach:.2f} K minimum approach"
            )

        self._thermal_duty_available = q_available

        self._thermal_duty_deficit = max(
            q_required - q_available,
            0.0,
        )

        self._thermal_feasible = (
            q_required <= q_available * (1.0 + 1e-9)
        )

        # ----------------------------------------------------------
        # Thermal feasibility warning
        # ----------------------------------------------------------

        if not self._thermal_feasible:
            deficit_kw = (
                self._thermal_duty_deficit / 1000.0
            )

            required_kw = q_required / 1000.0
            available_kw = q_available / 1000.0

            self._warn_with_category(
                "FEASIBILITY_WARNING",
                (
                    "Required phase-change duty exceeds heating-side "
                    "thermal capacity. "
                    f"Required={required_kw:.3f} kW, "
                    f"Available={available_kw:.3f} kW, "
                    f"Deficit={deficit_kw:.3f} kW; "
                    f"capacity basis: {available_basis}. "
                    "Required duty was NOT clipped."
                ),
            )

        # ----------------------------------------------------------
        # Determine design outlet temperature
        # ----------------------------------------------------------

        if self.boiling_side == "shell":
            # Normal ProcessPI configuration:
            # hot water in tubes, boiling fluid in shell.

            if self._thermal_feasible:
                th_out = (
                    hot["t_k"]
                    - q_required
                    / max(
                        hot["m_dot"] * hot["cp"],
                        1e-12,
                    )
                )

            elif explicit_heating_out is not None:
                # Keep the user's target outlet for LMTD sizing.
                th_out = explicit_heating_out

            else:
                # No feasible outlet target was supplied.
                # Stabilize at a small approach above the boiling
                # temperature so LMTD can still be calculated.
                minimum_approach = float(
                    self.specs.get(
                        "minimum_phase_change_approach",
                        0.5,
                    )
                )

                th_out = (
                    boiling_temperature
                    + minimum_approach
                )

            tc_out = cold["t_k"]

        else:
            # Boiling fluid in tubes.
            # Heating fluid is the cold stream in this assignment.

            th_out = hot["t_k"]

            if self._thermal_feasible:
                tc_out = (
                    cold["t_k"]
                    + q_required
                    / max(
                        cold["m_dot"] * cold["cp"],
                        1e-12,
                    )
                )

            elif explicit_heating_out is not None:
                tc_out = explicit_heating_out

            else:
                minimum_approach = float(
                    self.specs.get(
                        "minimum_phase_change_approach",
                        0.5,
                    )
                )

                tc_out = (
                    boiling_temperature
                    - minimum_approach
                )

        # ----------------------------------------------------------
        # Store current duty for boiling HTC
        # ----------------------------------------------------------

        self._current_q_watts = q_required

        self._debug(
            f"Required phase-change duty: "
            f"{q_required / 1000.0:.6f} kW"
        )

        self._debug(
            f"Available heating duty: "
            f"{q_available / 1000.0:.6f} kW"
        )

        self._debug(
            f"Thermal feasible: "
            f"{self._thermal_feasible}"
        )

        return (
            q_required,
            th_out,
            tc_out,
        )

    # ==============================================================
    # LMTD CORRECTION
    # ==============================================================

    def _calculate_ft(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> float:
        # Phase-change side remains approximately isothermal.
        return 1.0

    # ==============================================================
    # BOILING HTC
    # ==============================================================

    def _calculate_boiling_htc(
        self,
        boiling: Dict[str, float],
        q_flux: float,
    ) -> float:

        pressure = max(
            boiling.get(
                "p_bar",
                1.0,
            ),
            0.5,
        )

        h_boil = self._safe_float(
            BoilingHTC(
                heat_flux=max(
                    q_flux,
                    1e3,
                ),
                pressure=pressure,
            )
            .calculate()
            .to("W/m2K"),
            "h_boil",
        )

        orientation_factor = (
            1.1
            if self.orientation == "vertical"
            else 1.0
        )

        return max(
            1500.0,
            min(
                h_boil * orientation_factor,
                18000.0,
            ),
        )

    def _calculate_htc(
        self,
        dimless: Dict[str, float],
        geometry: Dict[str, float],
        tube: Dict[str, float],
        shell: Dict[str, float],
        **kwargs: Any,
    ):

        h_tube, h_shell = super()._calculate_htc(
            dimless,
            geometry,
            tube,
            shell,
        )

        hot, cold = self._hot_cold_props(
            tube,
            shell,
        )

        boiling = (
            hot
            if self.boiling_side == "tube"
            else cold
        )

        # IMPORTANT:
        # Use the actual calculated process duty.
        # Never use an arbitrary 1 MW fallback.
        q_watts = float(
            getattr(
                self,
                "_current_q_watts",
                0.0,
            )
        )

        if q_watts <= 0:
            q_watts = 1e3

        area = max(
            float(
                geometry.get(
                    "area",
                    1.0,
                )
            ),
            1e-9,
        )

        q_flux = max(
            q_watts / area,
            1e3,
        )

        h_boil = self._calculate_boiling_htc(
            boiling,
            q_flux,
        )

        if self.boiling_side == "tube":
            h_tube = h_boil
            h_shell = max(
                h_shell,
                220.0,
            )
        else:
            h_shell = h_boil
            h_tube = max(
                h_tube,
                250.0,
            )

        return h_tube, h_shell

    # ==============================================================
    # DESIGN CONSTRAINTS
    # ==============================================================

    def _validate_design_constraints(
        self,
        results: Dict[str, Any],
    ) -> None:

        limits = self.design_limits

        def _number(
            key: str,
            default: float = 0.0,
        ) -> float:

            value = results.get(
                key,
                default,
            )

            if value is None:
                return default

            return float(
                getattr(
                    value,
                    "value",
                    value,
                )
            )

        if _number("Area") > limits["max_area"]:
            self._warn_with_category(
                "GEOMETRY_WARNING",
                "Area exceeds configured evaporator design limit",
            )

        if _number("tube_count") > limits["max_tube_count"]:
            self._warn_with_category(
                "GEOMETRY_WARNING",
                "Tube count exceeds configured evaporator design limit",
            )

        if _number("shell_diameter") > limits["max_shell_diameter"]:
            self._warn_with_category(
                "GEOMETRY_WARNING",
                "Shell diameter exceeds configured evaporator design limit",
            )

        if _number("tube_velocity") < limits["min_tube_velocity"]:
            self._warn_with_category(
                "HYDRAULIC_WARNING",
                "Tube velocity below recommended minimum",
            )

        if _number("tube_velocity") > limits["max_tube_velocity"]:
            self._warn_with_category(
                "HYDRAULIC_WARNING",
                "Tube velocity above recommended maximum",
            )

        if _number("shell_velocity") < limits["min_shell_velocity"]:
            self._warn_with_category(
                "HYDRAULIC_WARNING",
                "Shell velocity below recommended minimum",
            )

        if _number("tube_velocity") < limits["target_tube_velocity"]:
            self._warn_with_category(
                "HYDRAULIC_WARNING",
                "Tube velocity below target tube velocity",
            )

        if _number("shell_velocity") < limits["target_shell_velocity"]:
            self._warn_with_category(
                "HYDRAULIC_WARNING",
                "Shell velocity below target shell velocity",
            )

    # ==============================================================
    # PRESSURE DROP
    # ==============================================================

    def _calculate_pressure_drop(
        self,
        geometry: Dict[str, float],
        tube: Dict[str, float],
        shell: Dict[str, float],
        shell_velocity: float | None = None,
        tube_velocity: float | None = None,
        **kwargs: Any,
    ):

        shell_velocity = (
            shell_velocity
            if shell_velocity is not None
            else float(
                kwargs.get(
                    "shell_velocity",
                    kwargs.get(
                        "v_shell",
                        0.0,
                    ),
                )
            )
        )

        tube_velocity = (
            tube_velocity
            if tube_velocity is not None
            else float(
                kwargs.get(
                    "tube_velocity",
                    kwargs.get(
                        "v_tube",
                        0.0,
                    ),
                )
            )
        )

        shell_passes = int(
            kwargs.get(
                "shell_passes",
                1,
            )
        )

        tube_passes = int(
            kwargs.get(
                "tube_passes",
                1,
            )
        )

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

        # ----------------------------------------------------------
        # Static head for vertical boiling service
        # ----------------------------------------------------------

        orientation = str(
            kwargs.get(
                "orientation",
                self.orientation,
            )
        ).lower()

        if orientation == "vertical":

            hot, cold = self._hot_cold_props(
                tube,
                shell,
            )

            boiling = (
                hot
                if self.boiling_side == "tube"
                else cold
            )

            rho = boiling.get(
                "density",
                900.0,
            )

            static_head = (
                rho
                * 9.81
                * max(
                    float(
                        geometry.get(
                            "tube_length",
                            6.0,
                        )
                    ),
                    0.0,
                )
            )

            if self.boiling_side == "tube":
                tube_dp += static_head
            else:
                shell_dp += static_head

        return tube_dp, shell_dp

    # ==============================================================
    # RESULT DECORATION
    # ==============================================================

    def _decorate_results(
        self,
        results: Dict[str, Any],
    ) -> Dict[str, Any]:

        self._validate_design_constraints(
            results
        )

        # ----------------------------------------------------------
        # Thermal feasibility
        # ----------------------------------------------------------

        if self._thermal_duty_required is not None:

            results["Q_required"] = (
                self._thermal_duty_required
            )

            results["Q_available"] = (
                self._thermal_duty_available
            )

            results["Q_deficit"] = (
                self._thermal_duty_deficit
            )

            results["thermal_duty_required_kW"] = (
                self._thermal_duty_required / 1000.0
            )

            results["thermal_duty_available_kW"] = (
                self._thermal_duty_available / 1000.0
            )

            results["thermal_duty_deficit_kW"] = (
                self._thermal_duty_deficit / 1000.0
            )

            results["thermal_duty_source"] = (
                self._thermal_duty_source
            )

            results["thermal_feasible"] = (
                self._thermal_feasible
            )

            if not self._thermal_feasible:

                # Thermal failure has priority over hydraulic
                # failure because the requested process duty itself
                # cannot be achieved.

                results["status"] = (
                    "THERMAL_FAILURE"
                )

                results["convergence_status"] = (
                    "THERMAL_FAILURE"
                )

                feasibility = results.get(
                    "feasibility_summary"
                )

                if isinstance(
                    feasibility,
                    dict,
                ):
                    feasibility["thermal_ok"] = False
                    feasibility["status"] = (
                        "THERMAL_FAILURE"
                    )

                self._warn_with_category(
                    "FEASIBILITY_WARNING",
                    (
                        "Thermal design failure: "
                        f"required duty "
                        f"{self._thermal_duty_required / 1000.0:.3f} kW "
                        f"> available heating duty "
                        f"{self._thermal_duty_available / 1000.0:.3f} kW."
                    ),
                )

        # ----------------------------------------------------------
        # Hydraulic feasibility must reflect the calculated velocities.
        # Do not report PASS merely because pressure-drop calculations ran.
        # ----------------------------------------------------------
        def _velocity_value(*keys):
            # Results may be returned as normalized payload keys or as
            # presentation-layer labels, depending on the design path.
            for key in keys:
                value = results.get(key)
                if value is not None:
                    try:
                        return float(value.to("m/s") if hasattr(value, "to") else value)
                    except (TypeError, ValueError, AttributeError):
                        continue
            # Some HX result wrappers keep the original design payload nested.
            for container_key in ("payload", "results", "design", "geometry"):
                nested = results.get(container_key)
                if isinstance(nested, dict):
                    for key in keys:
                        value = nested.get(key)
                        if value is not None:
                            try:
                                return float(value.to("m/s") if hasattr(value, "to") else value)
                            except (TypeError, ValueError, AttributeError):
                                continue
            return None

        tube_velocity = _velocity_value(
            "tube_velocity", "v_tube", "Tube Velocity", "tube velocity",
            "tube_velocity_m_s"
        )
        shell_velocity = _velocity_value(
            "shell_velocity", "v_shell", "Shell Velocity", "shell velocity",
            "shell_velocity_m_s"
        )
        limits = self.design_limits
        min_tube = limits["min_tube_velocity"]
        max_tube = limits["max_tube_velocity"]
        min_shell = limits["min_shell_velocity"]
        # Use an explicit max if provided; otherwise flag extreme shell
        # velocities rather than allowing a physically implausible PASS.
        max_shell = float(self.specs.get("max_shell_velocity", 2.0))
        feasibility = results.get("feasibility_summary")
        if not isinstance(feasibility, dict):
            feasibility = {}
            results["feasibility_summary"] = feasibility

        # Only recalculate hydraulic feasibility when this design path actually
        # supplies both velocities. Some reboiler result paths normalize the
        # velocities after decoration; treating missing values as real zeros
        # (or as automatic failure) creates misleading "None m/s" warnings and
        # can overwrite the pressure-drop assessment.
        if tube_velocity is not None and shell_velocity is not None:
            hydraulic_ok = (
                min_tube <= tube_velocity <= max_tube
                and min_shell <= shell_velocity <= max_shell
            )
            feasibility["hydraulic_ok"] = hydraulic_ok
            feasibility["hydraulic_feasible"] = hydraulic_ok
            if not hydraulic_ok and results.get("status") not in {"THERMAL_FAILURE"}:
                results["status"] = "HYDRAULIC_FAILURE"
                results["convergence_status"] = "HYDRAULIC_FAILURE"
                feasibility["status"] = "HYDRAULIC_FAILURE"
            if not hydraulic_ok:
                warning = (
                    "Calculated tube/shell velocity is outside configured hydraulic limits "
                    f"(tube={tube_velocity:.3f} m/s, shell={shell_velocity:.3f} m/s; "
                    f"tube range {min_tube}-{max_tube} m/s, shell range "
                    f"{min_shell}-{max_shell} m/s)."
                )
                if warning not in results.get("warnings", []):
                    results.setdefault("warnings", []).append(warning)

        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        results.update(
            {
                "hx_type": "evaporator",
                "service": "evaporator",
                "phase_change": True,
                "orientation": self.orientation,
                "boiling_side": self.boiling_side,
                "convergence_status": results.get(
                    "status",
                    "OK",
                ),
                "warnings": list(
                    dict.fromkeys(
                        [
                            *results.get(
                                "warnings",
                                [],
                            ),
                            *self._warnings,
                        ]
                    )
                ),
            }
        )

        # Rebuild warning details after adding our warnings.
        warnings = results["warnings"]

        results["warning_details"] = [
            {
                "category": (
                    w.split("]", 1)[0][1:]
                    if w.startswith("[")
                    and "]" in w
                    else "GENERAL_WARNING"
                ),
                "message": (
                    w.split("]", 1)[1].strip()
                    if w.startswith("[")
                    and "]" in w
                    else w
                ),
            }
            for w in warnings
        ]

        return results

    # ==============================================================
    # PUBLIC DESIGN / RATE
    # ==============================================================

    def design(self):
        self._current_q_watts = 0.0
        self._thermal_duty_required = None
        self._thermal_duty_available = None
        self._thermal_duty_deficit = None
        self._thermal_feasible = True
        self._thermal_duty_source = None

        return self._decorate_results(
            super().design()
        )

    def rate(self):
        self._current_q_watts = 0.0
        self._thermal_duty_required = None
        self._thermal_duty_available = None
        self._thermal_duty_deficit = None
        self._thermal_feasible = True
        self._thermal_duty_source = None

        return self._decorate_results(
            super().rate()
        )
