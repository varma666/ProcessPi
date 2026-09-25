from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from processpi.streams.material import MaterialStream
from processpi.units.area import Area
from processpi.units.heat_flow import HeatFlow
from processpi.units.heat_transfer_coefficient import HeatTransferCoefficient
from processpi.units.length import Length
from processpi.units.pressure import Pressure
from processpi.units.velocity import Velocity

from .base import HeatExchanger
from .condenser import CondenserHX
from .double_pipe import DoublePipeHX
from .evaporator import EvaporatorHX
from .reboiler import ReboilerHX
from .shell_and_tube import ShellAndTubeHX


@dataclass
class HeatExchangerResults:
    data: Dict[str, Any]

    def summary(self) -> str:
        """
        Return a formatted engineering summary of the heat exchanger results.
    
        The summary presents:
        - exchanger type and selection logic
        - calculation method
        - heat duty
        - heat-transfer area
        - overall heat-transfer coefficient
        - velocities
        - pressure drops
        - geometry
        - engineering status
        - engineering assessment
        - insights
        - warnings
        - recommendations
        """
    
        data = self.data
    
        # ==========================================================
        # HELPERS
        # ==========================================================
    
        def format_value(value, unit=None, decimals=3):
            """Format ProcessPI unit objects or numeric values safely."""
    
            if value is None:
                return "N/A"
    
            try:
                if unit and hasattr(value, "to"):
                    converted = value.to(unit)
    
                    raw = getattr(converted, "value", converted)
    
                    if isinstance(raw, (int, float)):
                        return f"{raw:.{decimals}f} {unit}"
    
                    return f"{raw} {unit}"
    
                if isinstance(value, (int, float)):
                    return f"{value:.{decimals}f}"
    
                return str(value)
    
            except Exception:
                return str(value)
    
        def format_pressure(value):
            """Display pressure in kPa."""
    
            return format_value(value, "kPa", 3)
    
        def format_area(value):
            """Display area in m²."""
    
            return format_value(value, "m2", 3)
    
        def format_length(value):
            """Display length in m."""
    
            return format_value(value, "m", 3)
    
        # ==========================================================
        # BASIC RESULTS
        # ==========================================================
    
        hx_type = data.get("hx_type", "UNKNOWN")
        method = data.get("method", "UNKNOWN")
    
        q = data.get("Q")
        area = data.get("Area")
        ucalc = data.get("U_calculated")
    
        tube_velocity = data.get("tube_velocity")
        shell_velocity = data.get("shell_velocity")
    
        tube_dp = data.get("tube_dp")
        shell_dp = data.get("shell_dp")
    
        tube_count = data.get("tube_count")
        tube_length = data.get("tube_length")
    
        status = data.get("status", "UNKNOWN")
    
        warnings = data.get("warnings") or []
        insights = data.get("engineering_insights") or []
        recommendations = data.get("recommendations") or []
    
        assessment = data.get("engineering_assessment")
    
        # ==========================================================
        # AUTOMATIC TYPE SELECTION
        # ==========================================================
    
        selection = data.get("hx_type_selection")
    
        if selection:
            selection_reason = selection.get("reason", "Automatic selection")
    
            type_selection = (
                f"auto\n"
                f"Reason                : {selection_reason}"
            )
        else:
            type_selection = "explicit"
    
        # ==========================================================
        # PRESSURE DROP LIMITS
        # ==========================================================
    
        specs = data.get("specs", {}) or {}
    
        tube_dp_limit = specs.get("tube_dp")
        shell_dp_limit = specs.get("shell_dp")
    
        # ==========================================================
        # STATUS CLASSIFICATION
        # ==========================================================
    
        thermal_ok = data.get("thermal_ok")
        hydraulic_ok = data.get("hydraulic_ok")
        pressure_drop_ok = data.get("pressure_drop_ok")
    
        feasibility = data.get("feasibility_summary")
    
        if isinstance(feasibility, dict):
            thermal_ok = feasibility.get("thermal_ok", thermal_ok)
            hydraulic_ok = feasibility.get("hydraulic_ok", hydraulic_ok)
            pressure_drop_ok = feasibility.get(
                "pressure_drop_ok",
                pressure_drop_ok,
            )
    
        # ==========================================================
        # SUMMARY HEADER
        # ==========================================================
    
        output = (
            "Heat Exchanger Summary\n"
            "==============================\n"
            f"Type                  : {hx_type}\n"
            f"Type Selection        : {type_selection}\n"
            f"Method                : {method}\n"
            f"Heat Duty             : {format_value(q, 'kW', 3)}\n"
            f"Area                  : {format_area(area)}\n"
            f"U Calculated          : {format_value(ucalc, 'W/m2K', 3)}\n"
            f"Tube Velocity         : {format_value(tube_velocity, 'm/s', 3)}\n"
            f"Shell Velocity        : {format_value(shell_velocity, 'm/s', 3)}\n"
            f"Tube Pressure Drop    : {format_pressure(tube_dp)}\n"
            f"Shell Pressure Drop   : {format_pressure(shell_dp)}\n"
            f"Tube Count            : {tube_count if tube_count is not None else 'N/A'}\n"
            f"Tube Length           : {format_length(tube_length)}\n"
            f"Status                : {status}\n"
        )
    
        # ==========================================================
        # PRESSURE DROP ASSESSMENT
        # ==========================================================
    
        if tube_dp_limit is not None or shell_dp_limit is not None:
    
            output += (
                "\n"
                "Pressure Drop Assessment\n"
                "------------------------------\n"
            )
    
            if tube_dp_limit is not None:
                output += (
                    f"Tube ΔP Limit        : "
                    f"{format_pressure(tube_dp_limit)}\n"
                )
    
                if tube_dp is not None:
                    output += (
                        f"Tube ΔP Actual       : "
                        f"{format_pressure(tube_dp)}\n"
                    )
    
            if shell_dp_limit is not None:
                output += (
                    f"Shell ΔP Limit       : "
                    f"{format_pressure(shell_dp_limit)}\n"
                )
    
                if shell_dp is not None:
                    output += (
                        f"Shell ΔP Actual      : "
                        f"{format_pressure(shell_dp)}\n"
                    )
    
        # ==========================================================
        # FEASIBILITY
        # ==========================================================
    
        if any(
            value is not None
            for value in (
                thermal_ok,
                hydraulic_ok,
                pressure_drop_ok,
            )
        ):
    
            output += (
                "\n"
                "Engineering Feasibility\n"
                "------------------------------\n"
            )
    
            if thermal_ok is not None:
                output += (
                    f"Thermal Performance  : "
                    f"{'PASS' if thermal_ok else 'FAIL'}\n"
                )
    
            if hydraulic_ok is not None:
                output += (
                    f"Hydraulic Performance: "
                    f"{'PASS' if hydraulic_ok else 'FAIL'}\n"
                )
    
            if pressure_drop_ok is not None:
                output += (
                    f"Pressure Drop        : "
                    f"{'PASS' if pressure_drop_ok else 'FAIL'}\n"
                )
    
        # ==========================================================
        # ENGINEERING ASSESSMENT
        # ==========================================================
    
        if assessment:
    
            output += (
                "\n"
                "Engineering Assessment\n"
                "------------------------------\n"
                f"{assessment}\n"
            )
    
        # ==========================================================
        # ENGINEERING INSIGHTS
        # ==========================================================
    
        if insights:
    
            output += (
                "\n"
                "Engineering Insights\n"
                "------------------------------\n"
            )
    
            for item in insights:
                output += f"• {item}\n"
    
        # ==========================================================
        # WARNINGS
        # ==========================================================
    
        if warnings:
    
            output += (
                "\n"
                "Warnings\n"
                "------------------------------\n"
            )
    
            for warning in warnings:
                output += f"• {warning}\n"
    
        # ==========================================================
        # RECOMMENDATIONS
        # ==========================================================
    
        if recommendations:
    
            output += (
                "\n"
                "Recommendations\n"
                "------------------------------\n"
            )
    
            for recommendation in recommendations:
                output += f"• {recommendation}\n"
    
        return output
    def detailed_summary(self) -> Dict[str, Any]:
        return self.data

    def trace(self) -> str:
        trace_entries = self.data.get("calculation_trace", [])
        grouped: Dict[str, list[dict[str, Any]]] = {}
        for entry in trace_entries:
            grouped.setdefault(entry.get("section", "GENERAL"), []).append(entry)
        lines: list[str] = []
        for section in ["THERMAL", "GEOMETRY", "HYDRAULICS", "DIMENSIONLESS", "PHASE_CHANGE", "GENERAL"]:
            rows = grouped.get(section, [])
            if not rows:
                continue
            lines.append("=" * 48)
            lines.append(section)
            lines.append("=" * len(section))
            for row in rows:
                lines.append(f"{row.get('name','item'):<24}: {row.get('value')}")
        return "\n".join(lines) if lines else "No engineering trace available."

    def debug_summary(self) -> Dict[str, Any]:
        warnings = self.data.get("warnings", [])
        return {
            "status": self.data.get("status"),
            "iterations": self.data.get("iterations"),
            "u_values": {
                "U_user": self.data.get("U_user"),
                "U_assumed": self.data.get("U_assumed"),
                "U_calculated": self.data.get("U_calculated"),
            },
            "velocities": {
                "tube_velocity": self.data.get("tube_velocity"),
                "shell_velocity": self.data.get("shell_velocity"),
            },
            "pressure_drop": {
                "tube_dp": self.data.get("tube_dp"),
                "shell_dp": self.data.get("shell_dp"),
            },
            "warning_count": len(warnings),
            "warnings": warnings,
            "optimization_actions": self.data.get("optimization_actions", []),
        }


class HeatExchangerEngine:
    # Automatic type selection, used only when no hx_type is given and the
    # streams show no phase change: the larger of the two inlet mass flows is
    # compared with this limit, and a flow at or below it gives a double pipe,
    # anything above it a shell and tube. 1 kg/s is the value the engine has
    # always used; it is a rule of thumb carried over from the original code, not
    # a sourced design criterion. Override it per run with the
    # `double_pipe_max_mass_flow` spec (MassFlowRate, or a number in kg/s).
    DOUBLE_PIPE_MAX_MASS_FLOW_KG_S = 1.0

    _map: Dict[str, Type[HeatExchanger]] = {
        "shell_and_tube": ShellAndTubeHX,
        "double_pipe": DoublePipeHX,
        "condenser": CondenserHX,
        "reboiler": ReboilerHX,
        "evaporator": EvaporatorHX,
        "bell_delaware": ShellAndTubeHX,
    }

    def __init__(self, name: Optional[str] = None, method: str = "kern", **kwargs: Any):
        self.name = name
        self.method = method.lower()
        if self.method not in {"kern", "bell_delaware"}:
            raise ValueError("method must be 'kern' or 'bell_delaware'")
        self.data: Dict[str, Any] = {}
        self._results: Optional[HeatExchangerResults] = None
        self._hx_type_selection: Optional[Dict[str, Any]] = None
        if kwargs:
            self.fit(**kwargs)

    def fit(
        self,
        hot_in: MaterialStream,
        cold_in: MaterialStream,
        hot_out: Optional[MaterialStream] = None,
        cold_out: Optional[MaterialStream] = None,
        hx_type: Optional[str] = None,
        **kwargs: Any,
    ):
    
        if (
            not isinstance(hot_in, MaterialStream)
            or not isinstance(cold_in, MaterialStream)
        ):
            raise TypeError(
                "hot_in and cold_in must "
                "be MaterialStream objects"
            )
    
        # An unknown type used to surface as a bare KeyError from `_map` in
        # run(); say which types exist instead, and say it here.
        if hx_type is not None:
            hx_type = self._check_hx_type(hx_type)

        # ======================================================
        # UPDATE METHOD IF PROVIDED
        # ======================================================
    
        method = kwargs.get("method")
    
        if method is not None:
    
            self.method = method.lower()
    
            if self.method not in {
                "kern",
                "bell_delaware",
            }:
    
                raise ValueError(
                    "method must be "
                    "'kern' or 'bell_delaware'"
                )
    
        # ======================================================
        # STORE DATA
        # ======================================================
    
        self.data = {
            "hot_in": hot_in,
            "cold_in": cold_in,
            "hot_out": hot_out,
            "cold_out": cold_out,
            "hx_type": hx_type,
            "specs": kwargs,
        }
    
        return self

    @classmethod
    def _check_hx_type(cls, hx_type: str) -> str:
        key = str(hx_type).lower()
        if key not in cls._map:
            raise ValueError(
                f"Unknown hx_type {hx_type!r}; expected one of {sorted(cls._map)}"
            )
        return key

    def _double_pipe_max_mass_flow(self) -> float:
        """The double pipe flow limit in kg/s: the spec if given, else the class default."""
        raw = self.data.get("specs", {}).get("double_pipe_max_mass_flow")
        if raw is None:
            return self.DOUBLE_PIPE_MAX_MASS_FLOW_KG_S
        value = float(getattr(raw.to("kg/s"), "value", raw.to("kg/s"))) if hasattr(raw, "to") else float(raw)
        if not value > 0.0:
            raise ValueError(
                f"double_pipe_max_mass_flow must be a positive mass flow, got {raw!r}"
            )
        return value

    def _select_hx_type(self) -> str:
        """
        Return the exchanger type to run, and record in `_hx_type_selection`
        whether it was chosen automatically and on what grounds (None when an
        explicit hx_type was given).
        """
        self._hx_type_selection = None
        explicit = self.data.get("hx_type")
        if explicit:
            return explicit
        hot_in = self.data["hot_in"]
        hot_out = self.data.get("hot_out")
        cold_out = self.data.get("cold_out")

        if hot_in.phase == "vapor" and hot_out and hot_out.phase == "liquid":
            self._hx_type_selection = {
                "auto_selected": True,
                "hx_type": "condenser",
                "criterion": "phase_change",
                "reason": "hot inlet is vapor and hot outlet is liquid",
            }
            return "condenser"
        if cold_out and cold_out.phase == "vapor":
            self._hx_type_selection = {
                "auto_selected": True,
                "hx_type": "reboiler",
                "criterion": "phase_change",
                "reason": "cold outlet is vapor",
            }
            return "reboiler"

        hot_m = float(getattr(hot_in.mass_flow().to("kg/s"), "value", hot_in.mass_flow().to("kg/s"))) if hot_in.mass_flow() else 0.0
        cold_m = float(getattr(self.data["cold_in"].mass_flow().to("kg/s"), "value", self.data["cold_in"].mass_flow().to("kg/s"))) if self.data["cold_in"].mass_flow() else 0.0
        threshold = self._double_pipe_max_mass_flow()
        flow = max(hot_m, cold_m)
        selected = "double_pipe" if flow <= threshold else "shell_and_tube"
        relation = "<=" if selected == "double_pipe" else ">"
        self._hx_type_selection = {
            "auto_selected": True,
            "hx_type": selected,
            "criterion": "max_stream_mass_flow",
            "hot_mass_flow_kg_s": hot_m,
            "cold_mass_flow_kg_s": cold_m,
            "max_stream_mass_flow_kg_s": flow,
            "double_pipe_max_mass_flow_kg_s": threshold,
            "reason": (
                f"no hx_type given; larger inlet mass flow {flow:.4g} kg/s "
                f"{relation} double pipe limit {threshold:.4g} kg/s"
            ),
        }
        return selected

    def run(self) -> HeatExchangerResults:
    
        # ======================================================
        # HX TYPE SELECTION
        # ======================================================
    
        hx_type = self._select_hx_type()
    
        if (
            hx_type == "shell_and_tube"
            and self.method == "bell_delaware"
        ):
            hx_type = "bell_delaware"
    
        cls = self._map[self._check_hx_type(hx_type)]
    
        # ======================================================
        # CREATE HX OBJECT
        # ======================================================
        specs = dict(self.data.get("specs", {}))
        
        # Prevent duplicate keyword issue
        specs.pop("method", None)
        # An engine-level setting, read by `_select_hx_type`, not an exchanger spec.
        specs.pop("double_pipe_max_mass_flow", None)
        
        hx = cls(
            hot_in=self.data["hot_in"],
            cold_in=self.data["cold_in"],
            hot_out=self.data.get("hot_out"),
            cold_out=self.data.get("cold_out"),
            method=(
                self.method
                if issubclass(cls, ShellAndTubeHX)
                else "kern"
            ),
            **specs,
        )
    
        # ======================================================
        # MODE SELECTION
        # ======================================================
    
        mode = (
            self.data
            .get("specs", {})
            .get("mode", "design")
            .lower()
        )
    
    
        # ======================================================
        # DESIGN MODE
        # ======================================================
    
        if mode == "design":
    
            results = hx.design()
    
        # ======================================================
        # RATE MODE
        # ======================================================
    
        elif mode == "rate":
    
            required_geometry = [
                "tube_od",
                "tube_id",
                "tube_length",
            ]
    
            missing = [
                key
                for key in required_geometry
                if key not in self.data.get("specs", {})
            ]
    
            if missing:
    
                raise ValueError(
                    "Rate mode requires fixed geometry. "
                    f"Missing: {missing}"
                )
    
            results = hx.rate()
    
        # ======================================================
        # INVALID MODE
        # ======================================================
    
        else:
    
            raise ValueError(
                f"Unsupported exchanger mode: {mode}"
            )
    
        # ======================================================
        # STORE RESULTS
        # ======================================================
    
        # Say that the type was picked automatically, and why; an explicit
        # hx_type leaves the results as the exchanger returned them.
        if self._hx_type_selection is not None:
            results["hx_type_selection"] = dict(self._hx_type_selection)
    
        self._results = HeatExchangerResults(results)
    
        return self._results

    def summary(self):
        if not self._results:
            return None
        return self._results.summary()

    def results(self):
        """
        Return the results of the last run.

        Raises:
            RuntimeError: If `run()` has not been called. `__init__` sets
                `_results` to None, so testing for the attribute never fired and
                the method returned None instead.
        """
        if self._results is None:
            raise RuntimeError("Run the model first using hx.run()")
        return self._results
