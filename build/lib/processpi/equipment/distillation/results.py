from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DistillationResults:
    """Results of DistillationColumn.design(); `data` holds every value, `summary()` formats them."""

    data: Dict[str, Any]

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def summary(self) -> str:
        d = self.data
        lines = []

        def fmt(value, unit=None, decimals=3):
            if value is None:
                return "N/A"
            if unit and hasattr(value, "to"):
                return f"{value.to(unit).original_value:.{decimals}f} {unit}"
            if isinstance(value, float):
                return f"{value:.{decimals}f}"
            return str(value)

        def section(title):
            lines.append("")
            lines.append(title)
            lines.append("-" * len(title))

        title = f"DISTILLATION COLUMN: {d.get('name', '')}"
        lines.append("=" * len(title))
        lines.append(title)
        lines.append("=" * len(title))
        lines.append(f"Method              : {d['method']} (Gilliland: {d['gilliland_correlation']})")
        lines.append(f"Keys                : light {d['light_key']}, heavy {d['heavy_key']}")
        lines.append(f"Pressure            : {fmt(d['pressure'], 'bar', 4)}")

        section("Material balance")
        names = list(d["feed"]["z"])
        width = max(len(n) for n in names + ["Component"])
        lines.append(f"{'Component':<{width}}  {'Feed z':>8}  {'Distillate x':>12}  {'Bottoms x':>10}  {'alpha (to HK)':>13}")
        for n in names:
            lines.append(
                f"{n:<{width}}  {d['feed']['z'][n]:8.4f}  {d['distillate']['x'][n]:12.4f}  "
                f"{d['bottoms']['x'][n]:10.4f}  {d['relative_volatility'][n]:13.4f}"
            )
        lines.append(f"Feed F              : {fmt(d['feed']['F'], 'kmol/h')}  (q = {d['feed']['q']:.3f}, {d['feed']['q_source']})")
        lines.append(f"Distillate D        : {fmt(d['distillate']['D'], 'kmol/h')}")
        lines.append(f"Bottoms B           : {fmt(d['bottoms']['B'], 'kmol/h')}")
        rec = d["key_recoveries"]
        lines.append(f"Key recoveries      : {rec['light_key_to_distillate'] * 100:.2f} % LK to distillate, "
                     f"{rec['heavy_key_to_bottoms'] * 100:.2f} % HK to bottoms")

        section("Stages and reflux")
        lines.append(f"Minimum stages      : {d['N_min']:.2f} (Fenske, reboiler included)")
        lines.append(f"Minimum reflux      : {d['R_min']:.3f} (Underwood)")
        for n, flow in d.get("underwood_distillate_at_R_min", {}).items():
            lines.append(f"  {n} distributes; at R_min its distillate flow is {fmt(flow, 'kmol/h')}")
        lines.append(f"Reflux ratio        : {d['reflux_ratio']:.3f} ({d['reflux_ratio_source']}, R/Rmin = {d['R_over_R_min']:.2f})")
        lines.append(f"Theoretical stages  : {d['N_theoretical']:.2f} (Gilliland, reboiler included)")
        lines.append(f"Rectifying/stripping: {d['N_rectifying']:.2f} / {d['N_stripping']:.2f} (Kirkbride)")
        lines.append(f"Feed stage          : {d['feed_stage']} from the top (theoretical)")
        mt = d.get("mccabe_thiele")
        if mt:
            if "error" in mt:
                lines.append(f"McCabe-Thiele check : not available ({mt['error']})")
            else:
                lines.append(f"McCabe-Thiele check : {mt['N_theoretical']} stages ({mt['N_fractional']:.2f} fractional), "
                             f"feed on stage {mt['feed_stage']} ({mt['equilibrium']})")

        if "actual_trays" in d:
            section("Trays")
            lines.append(f"Tray efficiency     : {d['tray_efficiency'] * 100:.1f} % ({d['tray_efficiency_source']})")
            lines.append(f"Actual trays        : {d['actual_trays']}")
            lines.append(f"Feed tray           : {d['feed_tray']} from the top")

        if "temperatures" in d:
            section("Temperatures and duties")
            t = d["temperatures"]
            lines.append(f"Condenser           : {fmt(t['condenser'], 'C', 2)}")
            lines.append(f"Top stage           : {fmt(t['top_stage'], 'C', 2)}")
            lines.append(f"Reboiler            : {fmt(t['reboiler'], 'C', 2)}")
            lines.append(f"Condenser duty      : {fmt(d['condenser_duty'], 'kW', 1)}")
            lines.append(f"Reboiler duty       : {fmt(d['reboiler_duty'], 'kW', 1)}")

        if "hydraulics" in d:
            section("Column sizing (tray column)")
            for name, h in d["hydraulics"].items():
                lines.append(
                    f"{name.capitalize():<7} F_LV {h['flow_parameter']:.3f}, C_sb {fmt(h['csb'], 'm/s')}, "
                    f"u_flood {fmt(h['flooding_velocity'], 'm/s')}, D {fmt(h['diameter'], 'm')}"
                )
            lines.append(f"Column diameter     : {fmt(d['diameter'], 'm')} (governed by the {d['diameter_governed_by']} section)")
            lines.append(f"Tray spacing        : {fmt(d['tray_spacing'], 'm', 2)}, design at {d['flood_fraction'] * 100:.0f} % of flooding")
            lines.append(f"Tray section height : {fmt(d['tray_section_height'], 'm', 2)} (without top and bottom allowances)")

        if d.get("assumptions"):
            section("Assumptions")
            lines.extend(f"- {a}" for a in d["assumptions"])
        if d.get("warnings"):
            section("Warnings")
            lines.extend(f"- {w}" for w in d["warnings"])
        return "\n".join(lines)
