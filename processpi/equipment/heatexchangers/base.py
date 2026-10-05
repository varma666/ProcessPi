from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from processpi.calculations.heat_transfer import HeatExchangerArea, LMTD, OverallHeatTransferCoefficient
from processpi.calculations.heat_transfer.hx_kern import LatentDuty, SensibleDuty
from processpi.equipment.base import Equipment
from processpi.streams.material import MaterialStream


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
        self._warnings.append(message)
        self.logger.warning(message)

    def _warn_with_category(self, category: str, message: str) -> None:
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

    def _resolve_stream_mass_flow(self, stream: MaterialStream) -> tuple[float | None, str]:
        """
        Resolve mass flow for a stream.
    
        Mass flow may be specified on either:
            1. The inlet stream
            2. The corresponding outlet stream
    
        Precedence:
            inlet mass flow > outlet mass flow > exchanger-level mass_flow_rate
    
        This prevents the exchanger from silently falling back to 1 kg/s when
        the user specified the process flow on the outlet stream.
    
        Returns:
            (mass_flow_kg_s, source)
        """
    
        if stream is None:
            return None, "none"
    
        # ---------------------------------------------------------
        # Determine corresponding outlet
        # ---------------------------------------------------------
        paired_outlet = None
    
        if stream is self.hot_in:
            paired_outlet = self.hot_out
        elif stream is self.cold_in:
            paired_outlet = self.cold_out
    
        # ---------------------------------------------------------
        # 1. Inlet mass flow
        # ---------------------------------------------------------
        inlet_mass_flow = None
    
        try:
            inlet_mass_flow = stream.mass_flow()
        except Exception:
            inlet_mass_flow = None
    
        if inlet_mass_flow is not None:
            inlet_value = self._safe_float(
                inlet_mass_flow.to("kg/s"),
                "mass_flow",
            )
    
            if inlet_value > 0:
                # If outlet flow is also specified, check consistency.
                if paired_outlet is not None:
                    try:
                        outlet_mass_flow = paired_outlet.mass_flow()
                    except Exception:
                        outlet_mass_flow = None
    
                    if outlet_mass_flow is not None:
                        outlet_value = self._safe_float(
                            outlet_mass_flow.to("kg/s"),
                            "outlet_mass_flow",
                        )
    
                        if outlet_value > 0:
                            relative_difference = abs(
                                inlet_value - outlet_value
                            ) / max(abs(inlet_value), 1e-12)
    
                            if relative_difference > 0.01:
                                self._warn_with_category(
                                    "FLOW_BALANCE_WARNING",
                                    (
                                        f"{stream.name}: inlet mass flow "
                                        f"{inlet_value:.6g} kg/s differs from "
                                        f"outlet mass flow {outlet_value:.6g} kg/s "
                                        f"by {relative_difference * 100:.2f}%; "
                                        f"inlet flow is used."
                                    ),
                                )
    
                return inlet_value, f"{stream.name}:inlet"
    
        # ---------------------------------------------------------
        # 2. Corresponding outlet mass flow
        # ---------------------------------------------------------
        if paired_outlet is not None:
            try:
                outlet_mass_flow = paired_outlet.mass_flow()
            except Exception:
                outlet_mass_flow = None
    
            if outlet_mass_flow is not None:
                outlet_value = self._safe_float(
                    outlet_mass_flow.to("kg/s"),
                    "outlet_mass_flow",
                )
    
                if outlet_value > 0:
                    return outlet_value, f"{paired_outlet.name}:outlet"
    
        # ---------------------------------------------------------
        # 3. Explicit exchanger-level fallback
        # ---------------------------------------------------------
        configured_flow = self.specs.get("mass_flow_rate")
    
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
                return configured_value, "exchanger_spec"
    
        # ---------------------------------------------------------
        # 4. Do NOT silently assume 1 kg/s
        # ---------------------------------------------------------
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
                f"'{s.name}'. Specify mass_flow on either the inlet or "
                f"outlet stream, or provide exchanger-level "
                f"mass_flow_rate."
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
    
        return {
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
        if self.hot_out and hot["t_k"] is not None and self.hot_out.temperature is not None:
            t_out = self._safe_float(self.hot_out.temperature.to("K"), "hot_out_temperature")
            return self._safe_float(SensibleDuty(m_dot=hot["m_dot"], cp=hot["cp"], t_in=hot["t_k"], t_out=t_out).calculate().to("W"), "sensible_duty_hot")
        if self.cold_out and cold["t_k"] is not None and self.cold_out.temperature is not None:
            t_in = self._safe_float(self.cold_out.temperature.to("K"), "cold_out_temperature")
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
