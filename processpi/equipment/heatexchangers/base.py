from __future__ import annotations

import copy
import logging
from typing import Any, Dict, Optional

from processpi.calculations.heat_transfer import HeatExchangerArea, LMTD, OverallHeatTransferCoefficient
from processpi.calculations.heat_transfer.hx_kern import LatentDuty, SensibleDuty
from processpi.equipment.base import Equipment
from processpi.streams.material import MaterialStream
from processpi.units.temperature import Temperature


class HeatExchangerBaseMixin:
    def _init_runtime(self) -> None:
        self.verbose = bool(self.specs.get("verbose", False))
        self.logger = self.specs.get("logger") or logging.getLogger(f"processpi.hx.{self.__class__.__name__.lower()}")
        self._warnings: list[str] = []
        self._calculation_trace: list[dict[str, Any]] = []

    def _debug(self, *args: object) -> None:
        if self.verbose:
            self.logger.debug(" ".join(str(a) for a in args))

    def _warn(self, message: str) -> None:
        if getattr(self, "_suppress_warnings", False):
            return
        self._warnings.append(message)
        self.logger.warning(message)

    def _warn_with_category(self, category: str, message: str) -> None:
        if getattr(self, "_suppress_warnings", False):
            return
        tagged = f"[{category}] {message}"
        if tagged in self._warnings:
            return
        self._warnings.append(tagged)
        # The design loop clears per-pass warnings on every pass; a warning
        # raised again on a later pass is not logged a second time.
        logged = self.__dict__.setdefault("_logged_warnings", set())
        if tagged not in logged:
            logged.add(tagged)
            self.logger.warning(tagged)

    def _trace_step(self, section: str, name: str, value: Any) -> None:
        entry = {"section": section, "name": name, "value": value}
        self._calculation_trace.append(entry)
        if self.verbose:
            self.logger.debug(f"[{section}] {name}: {value}")


class HeatExchanger(HeatExchangerBaseMixin, Equipment):
    """
    Two-stream heat exchanger with named ports ``hot_in``, ``cold_in``,
    ``hot_out`` and ``cold_out``, usable as a ``Flowsheet`` unit.

    ``simulate()`` closes the energy balance for the flowsheet solve.
    Sizing (``design()``/``rate()``) lives in the subclasses and is
    dispatched by ``HeatExchangerEngine``.
    """

    DUTY_SPECS = ("Q", "hot_out_temperature", "cold_out_temperature")

    def __init__(self, hot_in: Optional[MaterialStream] = None, cold_in: Optional[MaterialStream] = None, hot_out: Optional[MaterialStream] = None, cold_out: Optional[MaterialStream] = None, name: str = "HeatExchanger", **specs: Any):
        Equipment.__init__(
            self,
            name,
            inlet_ports=2,
            outlet_ports=2,
            inlet_names=["hot_in", "cold_in"],
            outlet_names=["hot_out", "cold_out"],
        )
        self.hot_in = hot_in
        self.cold_in = cold_in
        self.hot_out = hot_out
        self.cold_out = cold_out
        self.specs = specs
        self._init_runtime()

    # ------------------------
    # Named ports
    # ------------------------
    # The streams live in the Equipment port maps, so a stream connected
    # through Flowsheet.connect() is the same object design() reads.
    @property
    def hot_in(self) -> Optional[MaterialStream]:
        return self.inlets["hot_in"]

    @hot_in.setter
    def hot_in(self, stream: Optional[MaterialStream]) -> None:
        self.inlets["hot_in"] = stream

    @property
    def cold_in(self) -> Optional[MaterialStream]:
        return self.inlets["cold_in"]

    @cold_in.setter
    def cold_in(self, stream: Optional[MaterialStream]) -> None:
        self.inlets["cold_in"] = stream

    @property
    def hot_out(self) -> Optional[MaterialStream]:
        return self.outlets["hot_out"]

    @hot_out.setter
    def hot_out(self, stream: Optional[MaterialStream]) -> None:
        self.outlets["hot_out"] = stream

    @property
    def cold_out(self) -> Optional[MaterialStream]:
        return self.outlets["cold_out"]

    @cold_out.setter
    def cold_out(self, stream: Optional[MaterialStream]) -> None:
        self.outlets["cold_out"] = stream

    @staticmethod
    def _get_value(x, name):
        """
        Extract numeric value from floats or ProcessPI unit objects.
        """
        if hasattr(x, "value"):
            return x.value
        try:
            return float(x)
        except (TypeError, ValueError):
            raise TypeError(f"Could not interpret {name} value: {x!r}")

    def _safe_float(self, x: Any, name: str) -> float:
        return float(self._get_value(x, name))

    def _safe_positive(self, x: Any, name: str, minimum: float = 1e-12) -> float:
        value = self._safe_float(x, name)
        return max(value, minimum)

    def _safe_nonzero(self, x: Any, name: str, eps: float = 1e-12) -> float:
        value = self._safe_float(x, name)
        return value if abs(value) > eps else eps

    # ==============================================================
    # MASS-FLOW / ENERGY-BALANCE RESOLUTION
    # ==============================================================

    def _stream_for_side(self, side: str) -> Optional[MaterialStream]:
        """Return the inlet stream for a hot/cold side."""
        return self.hot_in if side == "hot" else self.cold_in

    def _outlet_for_side(self, side: str) -> Optional[MaterialStream]:
        """Return the outlet stream for a hot/cold side."""
        return self.hot_out if side == "hot" else self.cold_out

    def _direct_mass_flow(
        self,
        stream: Optional[MaterialStream],
    ) -> float | None:
        """
        Return explicitly supplied mass flow from a stream.

        This deliberately does NOT perform energy-balance resolution.
        It is used to determine which side is actually known.
        """
        if stream is None:
            return None

        try:
            mass_flow = stream.mass_flow()
        except Exception:
            mass_flow = None

        if mass_flow is None:
            return None

        value = self._safe_float(
            mass_flow.to("kg/s"),
            "mass_flow",
        )

        return value if value > 0 else None

    def _explicit_stream_temperature(
        self,
        stream: Optional[MaterialStream],
    ) -> float | None:
        """
        Return an explicitly supplied stream temperature in K.

        A MaterialStream can inherit its component's default temperature.
        That inherited value is not treated as a user-specified outlet target.
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
            "temperature",
        )

    def _stream_cp(self, stream: MaterialStream) -> float:
        """Return stream heat capacity in J/kg-K."""
        if stream is None:
            raise ValueError(
                f"{self.name}: stream is required to calculate heat capacity."
            )

        if getattr(stream, "specific_heat", None) is not None:
            return self._safe_float(
                stream.specific_heat.to("J/kgK"),
                "cp",
            )

        return self._safe_float(
            self.specs.get("cp", 4180.0),
            "cp",
        )

    def _latent_side_for_energy_balance(self) -> str | None:
        """
        Determine which side undergoes phase change.

        Returns:
            "hot", "cold", or None.
        """
        service = str(
            self.specs.get("service")
            or getattr(self, "service_type", "")
            or ""
        ).lower()

        # Condenser: hot stream condenses.
        if service in {
            "condenser",
            "total_condenser",
            "partial_condenser",
        }:
            return "hot"

        # Evaporator / reboiler:
        # respect the actual boiling-side configuration.
        if service in {
            "evaporator",
            "reboiler",
            "kettle_reboiler",
            "thermosyphon_reboiler",
        }:
            boiling_side = str(
                getattr(
                    self,
                    "boiling_side",
                    self.specs.get("boiling_side", "shell"),
                )
            ).lower()

            return "hot" if boiling_side == "tube" else "cold"

        # Explicit generic latent-side override.
        latent_side = self.specs.get("latent_side")
        if latent_side is not None:
            side = str(latent_side).lower()
            if side in {"hot", "cold"}:
                return side

        return None

    def _latent_heat_for_energy_balance(
        self,
        hot: Optional[Dict[str, float]] = None,
        cold: Optional[Dict[str, float]] = None,
    ) -> float | None:
        """
        Resolve latent heat in J/kg for energy-balance flow calculation.
        """
        latent_heat = self.specs.get("latent_heat")

        if latent_heat is not None:
            if hasattr(latent_heat, "to"):
                return self._safe_float(
                    latent_heat.to("J/kg"),
                    "latent_heat",
                )

            return self._safe_float(
                latent_heat,
                "latent_heat",
            )

        if hot is not None and cold is not None:
            return self._resolve_phase_change_latent_heat(
                hot,
                cold,
            )

        return None

    def _calculate_energy_balance_duty_from_known_side(
        self,
        known_side: str,
        known_mass_flow: float,
    ) -> tuple[float, str]:
        """
        Calculate heat duty from a side whose mass flow is known.

        Returns:
            (duty_W, basis)
        """
        if known_mass_flow <= 0:
            raise ValueError(
                f"{self.name}: known mass flow must be positive."
            )

        # ----------------------------------------------------------
        # Explicit Q has highest priority.
        # ----------------------------------------------------------

        if self.specs.get("Q") is not None:
            q = self._to_float(
                self.specs["Q"],
                "W",
            )

            if q <= 0:
                raise ValueError(
                    f"{self.name}: specified Q must be positive."
                )

            return abs(q), "specified_Q"

        latent_side = self._latent_side_for_energy_balance()

        # ----------------------------------------------------------
        # Phase-change side
        # ----------------------------------------------------------

        if latent_side == known_side:
            latent_heat = self._latent_heat_for_energy_balance()

            if latent_heat is None or latent_heat <= 0:
                raise ValueError(
                    f"{self.name}: cannot calculate phase-change duty "
                    "because latent_heat is unavailable."
                )

            q = known_mass_flow * latent_heat

            return q, (
                f"{known_side}_side_phase_change"
            )

        # ----------------------------------------------------------
        # Sensible side
        # ----------------------------------------------------------

        inlet = self._stream_for_side(known_side)
        outlet = self._outlet_for_side(known_side)

        if inlet is None:
            raise ValueError(
                f"{self.name}: {known_side} inlet stream is missing."
            )

        t_in = getattr(
            inlet,
            "temperature",
            None,
        )

        if t_in is None:
            raise ValueError(
                f"{self.name}: {known_side} inlet temperature is required "
                "to calculate the missing flow."
            )

        t_in_k = self._safe_float(
            t_in.to("K"),
            f"{known_side}_in_temperature",
        )

        t_out_k = self._explicit_stream_temperature(
            outlet
        )

        if t_out_k is None:
            raise ValueError(
                f"{self.name}: cannot calculate the missing flow on the "
                f"other side because {known_side}_out temperature is not "
                "specified. Provide the outlet temperature or Q."
            )

        delta_t = abs(
            t_in_k - t_out_k
        )

        if delta_t <= 1e-9:
            raise ValueError(
                f"{self.name}: {known_side} inlet and outlet temperatures "
                "are equal; sensible heat duty cannot be calculated."
            )

        cp = self._stream_cp(inlet)

        q = (
            known_mass_flow
            * cp
            * delta_t
        )

        return q, (
            f"{known_side}_side_sensible"
        )

    def _calculate_missing_side_mass_flow(
        self,
        missing_side: str,
        known_side: str,
        known_mass_flow: float,
    ) -> tuple[float, str]:
        """
        Calculate the missing side mass flow from an energy balance.

        Examples
        --------
        Reboiler:

            chlorine flow known
            ->
            Q = m_chlorine * latent_heat
            ->
            water flow = Q / (Cp * deltaT)

        Reverse case:

            water flow known
            ->
            Q = m_water * Cp * deltaT
            ->
            chlorine flow = Q / latent_heat
        """

        q_watts, duty_basis = (
            self._calculate_energy_balance_duty_from_known_side(
                known_side=known_side,
                known_mass_flow=known_mass_flow,
            )
        )

        latent_side = (
            self._latent_side_for_energy_balance()
        )

        # ----------------------------------------------------------
        # Missing side is phase change
        # ----------------------------------------------------------

        if missing_side == latent_side:
            latent_heat = (
                self._latent_heat_for_energy_balance()
            )

            if latent_heat is None or latent_heat <= 0:
                raise ValueError(
                    f"{self.name}: latent heat is required to calculate "
                    f"the {missing_side}-side phase-change flow."
                )

            missing_flow = (
                q_watts / latent_heat
            )

            return (
                missing_flow,
                (
                    f"energy_balance:{known_side}"
                    f"->{missing_side}:latent"
                ),
            )

        # ----------------------------------------------------------
        # Missing side is sensible
        # ----------------------------------------------------------

        inlet = self._stream_for_side(
            missing_side
        )

        outlet = self._outlet_for_side(
            missing_side
        )

        if inlet is None:
            raise ValueError(
                f"{self.name}: {missing_side} inlet stream is missing."
            )

        t_in = getattr(
            inlet,
            "temperature",
            None,
        )

        if t_in is None:
            raise ValueError(
                f"{self.name}: {missing_side} inlet temperature is "
                "required to calculate the missing flow."
            )

        t_in_k = self._safe_float(
            t_in.to("K"),
            f"{missing_side}_in_temperature",
        )

        t_out_k = self._explicit_stream_temperature(
            outlet
        )

        if t_out_k is None:
            raise ValueError(
                f"{self.name}: cannot calculate {missing_side} mass flow "
                f"from the energy balance because {missing_side}_out "
                "temperature is not specified."
            )

        delta_t = abs(
            t_in_k - t_out_k
        )

        if delta_t <= 1e-9:
            raise ValueError(
                f"{self.name}: {missing_side} inlet and outlet "
                "temperatures are equal; cannot calculate mass flow."
            )

        cp = self._stream_cp(
            inlet
        )

        missing_flow = (
            q_watts
            / max(cp * delta_t, 1e-12)
        )

        if missing_flow <= 0:
            raise ValueError(
                f"{self.name}: calculated {missing_side} mass flow "
                "is not positive."
            )

        return (
            missing_flow,
            (
                f"energy_balance:{known_side}"
                f"->{missing_side}:sensible"
            ),
        )

    def _resolve_stream_mass_flow(
        self,
        stream: MaterialStream,
    ) -> tuple[float | None, str]:
        """
        Resolve mass flow for a stream.

        Priority
        --------
        1. Explicit inlet flow
        2. Explicit corresponding outlet flow
        3. Energy-balance calculation from the opposite side
        4. Explicit exchanger-level mass_flow_rate

        The important rule is:

            A flow is NOT required on every stream.

        If one process side has a known flow and enough thermal information
        exists, ProcessPI calculates the other side's flow from the energy
        balance.
        """

        if stream is None:
            return None, "none"

        # ----------------------------------------------------------
        # Identify side
        # ----------------------------------------------------------

        if stream is self.hot_in:
            side = "hot"
            paired_outlet = self.hot_out
            other_side = "cold"

        elif stream is self.cold_in:
            side = "cold"
            paired_outlet = self.cold_out
            other_side = "hot"

        else:
            return None, "unknown"

        # ----------------------------------------------------------
        # 1. Explicit inlet flow
        # ----------------------------------------------------------

        inlet_value = self._direct_mass_flow(
            stream
        )

        if inlet_value is not None:

            # Check outlet consistency when both are explicitly supplied.
            outlet_value = self._direct_mass_flow(
                paired_outlet
            )

            if outlet_value is not None:
                relative_difference = (
                    abs(inlet_value - outlet_value)
                    / max(abs(inlet_value), 1e-12)
                )

                if relative_difference > 0.01:
                    self._warn_with_category(
                        "FLOW_BALANCE_WARNING",
                        (
                            f"{stream.name}: inlet mass flow "
                            f"{inlet_value:.6g} kg/s differs from "
                            f"outlet mass flow {outlet_value:.6g} kg/s "
                            f"by {relative_difference * 100:.2f}%; "
                            "inlet flow is used."
                        ),
                    )

            return (
                inlet_value,
                f"{stream.name}:inlet",
            )

        # ----------------------------------------------------------
        # 2. Explicit outlet flow
        # ----------------------------------------------------------

        outlet_value = self._direct_mass_flow(
            paired_outlet
        )

        if outlet_value is not None:
            return (
                outlet_value,
                f"{paired_outlet.name}:outlet",
            )

        # ----------------------------------------------------------
        # 3. Calculate from opposite-side energy balance
        # ----------------------------------------------------------

        other_stream = (
            self.hot_in
            if other_side == "hot"
            else self.cold_in
        )

        other_outlet = (
            self.hot_out
            if other_side == "hot"
            else self.cold_out
        )

        known_flow = self._direct_mass_flow(
            other_stream
        )

        if known_flow is None:
            known_flow = self._direct_mass_flow(
                other_outlet
            )

        if known_flow is not None:
            calculated_flow, source = (
                self._calculate_missing_side_mass_flow(
                    missing_side=side,
                    known_side=other_side,
                    known_mass_flow=known_flow,
                )
            )

            self._warn_with_category(
                "FLOW_BALANCE_INFO",
                (
                    f"{self.name}: calculated {side}-side mass flow "
                    f"{calculated_flow:.6g} kg/s from energy balance "
                    f"using {other_side}-side flow "
                    f"{known_flow:.6g} kg/s."
                ),
            )

            return calculated_flow, source

        # ----------------------------------------------------------
        # 4. Explicit exchanger-level flow
        # ----------------------------------------------------------

        configured_flow = (
            self.specs.get("mass_flow_rate")
        )

        if configured_flow is not None:

            configured_value = (
                self._safe_float(
                    configured_flow.to("kg/s"),
                    "mass_flow_rate",
                )
                if hasattr(configured_flow, "to")
                else self._safe_float(
                    configured_flow,
                    "mass_flow_rate",
                )
            )

            if configured_value > 0:
                return (
                    configured_value,
                    "exchanger_spec",
                )

        # ----------------------------------------------------------
        # 5. No flow and insufficient energy information
        # ----------------------------------------------------------

        return None, "missing"
    
    
    def _stream_props(self, s: MaterialStream) -> Dict[str, float]:
        """
        Build normalized stream properties for exchanger calculations.
    
        Mass flow is resolved from either the inlet or the corresponding
        outlet stream. The exchanger no longer silently assumes 1 kg/s
        when a process flow has not been supplied.
        """
    
        if s is None:
            raise ValueError(
                f"{self.name}: connect the hot_in and cold_in streams "
                "before sizing the exchanger."
            )
    
        mass_flow, mass_flow_source = self._resolve_stream_mass_flow(s)
        
        if mass_flow is None:
            raise ValueError(
                f"{self.name}: mass flow is missing for stream "
                f"'{s.name}'. Specify a flow on at least one stream "
                "side, or provide exchanger-level mass_flow_rate. "
                "If only one side flow is supplied, ProcessPI will "
                "calculate the other side from the energy balance "
                "when sufficient thermal information is available."
                
            )
    
        if mass_flow <= 0:
            raise ValueError(
                f"{self.name}: mass flow for stream '{s.name}' "
                f"must be positive."
            )
    
        temperature = (
            self._safe_float(
                s.temperature.to("K"),
                "t_k",
            )
            if s.temperature
            else None
        )
    
        if temperature is None:
            raise ValueError(
                f"{self.name}: temperature is missing for stream '{s.name}'."
            )
    
        pressure_bar = (
            self._to_float(s.pressure, "Pa") / 1e5
            if s.pressure
            else 1.0
        )
    
        props = {
            "density": self._safe_float(
                s.density.to("kg/m3"),
                "density",
            ),
    
            "viscosity": (
                self._safe_float(
                    s.component.viscosity().to("Pa·s"),
                    "viscosity",
                )
                if s.component and hasattr(s.component, "viscosity")
                else self._safe_float(
                    self.specs.get("viscosity", 1e-3),
                    "viscosity",
                )
            ),
    
            "cp": (
                self._safe_float(
                    s.specific_heat.to("J/kgK"),
                    "cp",
                )
                if s.specific_heat
                else self._safe_float(
                    self.specs.get("cp", 4180.0),
                    "cp",
                )
            ),
    
            "k": (
                self._safe_float(
                    s.component.thermal_conductivity().to("W/mK"),
                    "k",
                )
                if s.component
                and hasattr(s.component, "thermal_conductivity")
                else self._safe_float(
                    self.specs.get(
                        "thermal_conductivity",
                        0.6,
                    ),
                    "k",
                )
            ),
    
            "m_dot": mass_flow,
            "m_dot_source": mass_flow_source,
    
            "p_bar": pressure_bar,
    
            "phase": (
                s.phase or "liquid"
            ).lower(),
    
            "t_k": temperature,
        }
        self._evaluate_props(props, s, temperature)
        return props

    def _evaluate_props(self, props: Dict[str, Any], s: MaterialStream, t_k: float) -> None:
        """
        Set density, viscosity, cp and k in ``props`` to the component's values
        at ``t_k``, the stream pressure and the phase in ``props["phase"]``.

        These used to be read from the component at its default 25 C (and,
        for density, in whatever phase the vapour pressure test gave at
        1 atm), whatever the stream temperature. A density or specific heat
        given on the stream is kept; a stream without a component keeps the
        values it was built with.
        """
        component = getattr(s, "component", None)
        if component is None:
            return
        state = copy.copy(component)
        state.temperature = Temperature(t_k, "K")
        if getattr(s, "pressure", None) is not None:
            state.pressure = s.pressure
        resolved = "gas" if props["phase"] in {"vapor", "vapour", "gas", "steam"} else "liquid"
        if hasattr(state, "_phase"):
            state._phase = resolved
        # The stream's own component (a copy the stream owns) takes the phase
        # the exchanger works with, so its hx_data() lookups (velocity band,
        # fouling, U category) agree with these properties. A stream with no
        # stated phase is taken as liquid, and benzene at 90 C and the default
        # 1 atm would otherwise come out as vapour there.
        if hasattr(component, "_phase"):
            component._phase = resolved

        if getattr(s, "given_density", None) is None and hasattr(state, "density"):
            props["density"] = self._safe_float(state.density().to("kg/m3"), "density")
        if hasattr(state, "viscosity"):
            props["viscosity"] = self._safe_float(state.viscosity().to("Pa·s"), "viscosity")
        if getattr(s, "given_specific_heat", None) is None and hasattr(state, "specific_heat"):
            props["cp"] = self._safe_float(state.specific_heat().to("J/kgK"), "cp")
        if hasattr(state, "thermal_conductivity"):
            props["k"] = self._safe_float(state.thermal_conductivity().to("W/mK"), "k")
        props["t_props_k"] = t_k

    def _property_basis(self, hot: Dict[str, Any], cold: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """The temperature, phase and physical properties each side was designed on."""
        def side(props):
            return {
                "temperature_K": props.get("t_props_k", props["t_k"]),
                "phase": props["phase"],
                "density_kg_m3": props["density"],
                "viscosity_Pa_s": props["viscosity"],
                "cp_J_kgK": props["cp"],
                "k_W_mK": props["k"],
            }
        return {"hot": side(hot), "cold": side(cold)}

    def _evaluate_props_at_mean_temperature(self, hot: Dict[str, Any], cold: Dict[str, Any],
                                            th_out: float, tc_out: float) -> None:
        """
        Re-evaluate both sides' properties at their mean temperature,
        (inlet + outlet) / 2, the basis of the Kern method. ``t_k`` stays the
        inlet temperature.
        """
        self._evaluate_props(hot, self.hot_in, 0.5 * (hot["t_k"] + th_out))
        self._evaluate_props(cold, self.cold_in, 0.5 * (cold["t_k"] + tc_out))

    def _to_float(self, value: Any, unit: str | None = None) -> float:
        if hasattr(value, "to") and callable(value.to):
            converted = value.to(unit) if unit else value
            return float(getattr(converted, "value", converted))
        return float(value)

    def _wrap_length(self, value: float, unit: str = "m"):
        from processpi.units.length import Length
        return Length(float(value), unit)

    def _wrap_pressure(self, value: float, unit: str = "Pa"):
        from processpi.units.pressure import Pressure
        return Pressure(float(value), unit)

    def _wrap_velocity(self, value: float, unit: str = "m/s"):
        from processpi.units.velocity import Velocity
        return Velocity(float(value), unit)

    def _wrap_area(self, value: float, unit: str = "m2"):
        from processpi.units.area import Area
        return Area(float(value), unit)

    def _wrap_u(self, value: float, unit: str = "W/m2K"):
        from processpi.units.heat_transfer_coefficient import HeatTransferCoefficient
        return HeatTransferCoefficient(float(value), unit)

    def _wrap_heat(self, value: float, unit: str = "W"):
        from processpi.units.heat_flow import HeatFlow
        return HeatFlow(float(value), unit)

    def _lookup_steam_latent_heat(self, pressure_bar: float) -> float:
        """Approximate saturated steam latent heat [J/kg] using simple interpolation table."""
        table = [
            (1.0, 2257000.0),
            (2.0, 2202000.0),
            (3.0, 2163000.0),
            (5.0, 2108000.0),
            (8.0, 2048000.0),
            (10.0, 2014000.0),
            (15.0, 1944000.0),
            (20.0, 1889000.0),
        ]
        p = max(float(pressure_bar), 0.5)
        if p <= table[0][0]:
            return table[0][1]
        if p >= table[-1][0]:
            return table[-1][1]
        for (p1, h1), (p2, h2) in zip(table[:-1], table[1:]):
            if p1 <= p <= p2:
                ratio = (p - p1) / (p2 - p1)
                return h1 + ratio * (h2 - h1)
        return table[3][1]

    def _resolve_phase_change_latent_heat(self, hot: Dict[str, float], cold: Dict[str, float]) -> float | None:
        explicit_latent = self.specs.get("latent_heat")
        if explicit_latent is not None:
            return float(explicit_latent)

        service = str(self.specs.get("service") or getattr(self, "service_type", "")).lower()
        hot_in_phase = hot.get("phase", "liquid")
        cold_in_phase = cold.get("phase", "liquid")
        hot_out_phase = str(self.specs.get("hot_out_phase", hot_in_phase)).lower()
        cold_out_phase = str(self.specs.get("cold_out_phase", cold_in_phase)).lower()

        hot_condensing = hot_in_phase == "vapor" and hot_out_phase == "liquid"
        cold_boiling = cold_in_phase == "liquid" and cold_out_phase == "vapor"
        service_phase_change = service in {"condenser", "reboiler", "evaporator"}

        if hot_condensing or service == "condenser":
            return self._lookup_steam_latent_heat(hot.get("p_bar", 1.0))
        if cold_boiling or service_phase_change:
            if cold_in_phase == "steam" or getattr(self.cold_in.component, "name", "").lower() == "steam":
                return self._lookup_steam_latent_heat(cold.get("p_bar", 1.0))
            return 2257000.0
        return None

    def _is_phase_change_service(self) -> bool:
        service = str(self.specs.get("service") or getattr(self, "service_type", "")).lower()
        return service in {"condenser", "reboiler", "evaporator"}

    def _get_stream_outlet_phase(self, side: str, default_phase: str) -> str:
        if side == "hot":
            stream = self.hot_out
            spec_key = "hot_out_phase"
        else:
            stream = self.cold_out
            spec_key = "cold_out_phase"
        if stream is not None and getattr(stream, "phase", None):
            return str(stream.phase).lower()
        return str(self.specs.get(spec_key, default_phase)).lower()

    def _available_thermal_capacity(self, side: str, inlet: Dict[str, float], other_inlet_tk: float) -> float:
        in_phase = str(inlet.get("phase", "liquid")).lower()
        out_phase = self._get_stream_outlet_phase(side, in_phase)
        if in_phase != out_phase:
            latent = self._resolve_phase_change_latent_heat(inlet if side == "hot" else {"phase":"liquid"}, inlet if side == "cold" else {"phase":"liquid"})
            if latent is None:
                latent = 2257000.0
            return inlet["m_dot"] * latent
        return inlet["m_dot"] * inlet["cp"] * max(inlet["t_k"] - other_inlet_tk, 0.5)

    def heat_duty(self, hot: Dict[str, float], cold: Dict[str, float]) -> float:
        """Heat duty in W. A `Q` spec may be a HeatFlow or a number in W."""
        if self.specs.get("Q") is not None:
            return self._to_float(self.specs["Q"], "W")
        latent_heat = self._resolve_phase_change_latent_heat(hot, cold)
        if latent_heat is not None:
            latent_side = str(self.specs.get("latent_side", "hot")).lower()
            m_dot = hot["m_dot"] if latent_side == "hot" else cold["m_dot"]
            return self._safe_float(LatentDuty(m_dot=m_dot, latent_heat=latent_heat).calculate().to("W"), "latent_duty")
        # An outlet built without a temperature carries its component's 25 C
        # default; that is not a specification and must not set the duty.
        t_out = self._explicit_stream_temperature(self.hot_out)
        if hot["t_k"] is not None and t_out is not None:
            return self._safe_float(SensibleDuty(m_dot=hot["m_dot"], cp=hot["cp"], t_in=hot["t_k"], t_out=t_out).calculate().to("W"), "sensible_duty_hot")
        t_in = self._explicit_stream_temperature(self.cold_out)
        if cold["t_k"] is not None and t_in is not None:
            return self._safe_float(SensibleDuty(m_dot=cold["m_dot"], cp=cold["cp"], t_in=t_in, t_out=cold["t_k"]).calculate().to("W"), "sensible_duty_cold")
        raise ValueError("Insufficient thermal specification. Provide one outlet stream or Q/latent_heat.")

    def lmtd(self, th_in: float, th_out: float, tc_in: float, tc_out: float) -> float:
        return LMTD(dT1=th_in - tc_out, dT2=th_out - tc_in).calculate()

    def area(self, q_w: float, u: float, dtlm: float) -> float:
        return self._safe_float(HeatExchangerArea(heat_duty=q_w, overall_heat_transfer_coeff=u, log_mean_temp_diff=dtlm).calculate().to("m2"), "area")

    def overall_u(self, h_tube: float, h_shell: float, fouling_factor: float = 0.0) -> float:
        u = OverallHeatTransferCoefficient(resistances=[1.0 / h_tube, fouling_factor, 1.0 / h_shell]).calculate()
        return self._safe_float(u.to("W/m2K"), "overall_u")

    def design(self) -> Dict[str, Any]:
        raise NotImplementedError(
            f"{type(self).__name__} has no sizing method; use ShellAndTubeHX, DoublePipeHX, "
            "CondenserHX, ReboilerHX, EvaporatorHX or HeatExchangerEngine to design an exchanger."
        )

    # ------------------------
    # Flowsheet simulation
    # ------------------------
    def _wrap_temperature(self, value: float, unit: str = "K"):
        from processpi.units.temperature import Temperature
        return Temperature(float(value), unit)

    def _inlet_state(self, port: str) -> Dict[str, float]:
        """Temperature [K], mass flow [kg/s] and cp [J/kgK] of an inlet, all required."""
        stream = self.inlets[port]
        if stream is None:
            raise ValueError(f"{self.name}: inlet port '{port}' is not connected.")
        missing = []
        if stream.temperature is None:
            missing.append("temperature")
        if stream.mass_flow() is None:
            missing.append("mass flow")
        if stream.specific_heat is None:
            missing.append("specific heat")
        if missing:
            raise ValueError(f"{self.name}: inlet '{port}' (stream {stream.name!r}) has no {', '.join(missing)}.")
        state = {
            "t_k": self._to_float(stream.temperature, "K"),
            "m_dot": self._to_float(stream.mass_flow(), "kg/s"),
            "cp": self._to_float(stream.specific_heat, "J/kgK"),
        }
        if state["m_dot"] <= 0.0 or state["cp"] <= 0.0:
            raise ValueError(f"{self.name}: inlet '{port}' needs a positive mass flow and specific heat.")
        return state

    def _has_phase_change(self) -> bool:
        if self._is_phase_change_service() or self.specs.get("latent_heat") is not None:
            return True
        for side, stream in (("hot", self.hot_in), ("cold", self.cold_in)):
            in_phase = str(stream.phase or "liquid").lower()
            out_phase = self.specs.get(f"{side}_out_phase")
            if out_phase is not None and str(out_phase).lower() != in_phase:
                return True
        return False

    def _write_outlet(self, port: str, inlet: MaterialStream, t_out_k: float) -> MaterialStream:
        """
        Copy the inlet onto the outlet stream at the new temperature.

        Mass, composition, phase and pressure carry over unchanged: simulate()
        is a sensible-heat energy balance with no pressure-drop model.
        """
        outlet = self.outlets[port]
        outlet.component = inlet.component
        outlet.components = dict(inlet.components)
        outlet.molecular_weights = dict(inlet.molecular_weights)
        outlet.basis = inlet.basis
        outlet.phase = inlet.phase
        outlet.pressure = inlet.pressure
        outlet.temperature = self._wrap_temperature(t_out_k, "K")
        outlet.specific_heat = inlet.specific_heat
        outlet.density = inlet.density
        outlet._mass_flow = inlet.mass_flow()
        outlet._molar_flow = inlet._molar_flow
        # The inlet volumetric flow does not hold at the outlet temperature.
        outlet.flow_rate = None
        return outlet

    def simulate(self) -> Dict[str, Any]:
        """
        Solve the exchanger as a flowsheet unit.

        Exactly one duty spec is required: ``Q`` (HeatFlow or W),
        ``hot_out_temperature`` or ``cold_out_temperature`` (Temperature or K).
        Both sides then follow from Q = m_h cp_h (Th_in - Th_out)
        = m_c cp_c (Tc_out - Tc_in), and the results are written to the
        streams on the ``hot_out`` and ``cold_out`` ports.
        """
        given = [key for key in self.DUTY_SPECS if self.specs.get(key) is not None]
        if len(given) != 1:
            raise ValueError(f"{self.name}: simulate() needs exactly one of {list(self.DUTY_SPECS)}, got {given}.")
        hot = self._inlet_state("hot_in")
        cold = self._inlet_state("cold_in")
        # Check both outlets before writing either, so a failed solve leaves no half-updated streams.
        for port in ("hot_out", "cold_out"):
            if self.outlets[port] is None:
                raise ValueError(f"{self.name}: outlet port '{port}' is not connected.")
        if self._has_phase_change():
            raise NotImplementedError(f"{self.name}: simulate() handles sensible heat only; phase change is not supported yet.")
        if hot["t_k"] <= cold["t_k"]:
            raise ValueError(f"{self.name}: hot inlet ({hot['t_k']} K) must be hotter than cold inlet ({cold['t_k']} K).")
        c_hot = hot["m_dot"] * hot["cp"]
        c_cold = cold["m_dot"] * cold["cp"]

        spec = given[0]
        if spec == "Q":
            q_w = self._to_float(self.specs["Q"], "W")
        elif spec == "hot_out_temperature":
            q_w = c_hot * (hot["t_k"] - self._to_float(self.specs[spec], "K"))
        else:
            q_w = c_cold * (self._to_float(self.specs[spec], "K") - cold["t_k"])

        # Second law: no exchanger can move more than C_min (Th_in - Tc_in).
        q_max = min(c_hot, c_cold) * (hot["t_k"] - cold["t_k"])
        if q_w < 0.0 or q_w > q_max:
            raise ValueError(f"{self.name}: duty {q_w:.6g} W from {spec} is outside the feasible range 0 to {q_max:.6g} W.")

        th_out = hot["t_k"] - q_w / c_hot
        tc_out = cold["t_k"] + q_w / c_cold
        self._write_outlet("hot_out", self.hot_in, th_out)
        self._write_outlet("cold_out", self.cold_in, tc_out)
        self._trace_step("THERMAL", "flowsheet_duty_W", q_w)

        return {
            "Q": self._wrap_heat(q_w, "W"),
            "hot_out_temperature": self.hot_out.temperature,
            "cold_out_temperature": self.cold_out.temperature,
            "effectiveness": q_w / q_max,
        }
