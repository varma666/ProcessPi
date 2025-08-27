from typing import Dict, Any, List, Optional
from tabulate import tabulate

class PipelineResults:
    """Manages pipeline simulation results with summaries and detailed component breakdowns."""

    def __init__(self, results: Dict[str, Any]):
        self.results: Dict[str, Any] = results
        self._all_simulation_results = results.get("all_simulation_results", [])
        self._target_dp = results.get("target_dp")

    def __bool__(self) -> bool:
        return bool(self.results)

    # -------------------- Formatting helpers --------------------
    @staticmethod
    def _format_pressure(val: Optional[Any]) -> str:
        if val is None:
            return "N/A"
        v = getattr(val, "value", val)
        if v >= 1e6:
            return f"{v / 1e6:.2f} MPa"
        elif v >= 1e3:
            return f"{v / 1e3:.2f} kPa"
        return f"{v:.2f} Pa"

    @staticmethod
    def _format_power(val: Optional[Any]) -> str:
        if val is None:
            return "N/A"
        v = getattr(val, "value", val)
        if v >= 1e3:
            return f"{v / 1e3:.2f} kW"
        return f"{v:.2f} W"

    @staticmethod
    def _get_value(val: Any) -> Any:
        return getattr(val, "value", val)

    # -------------------- Main summaries --------------------
    def summary(self, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        if top_n is None or top_n == 1:
            optimum_result = self.get_optimum_result()
            if not optimum_result:
                print("No optimum result found.")
                return []

            summary_data = optimum_result.get("summary", {})
            residual_dp = optimum_result.get("residual_dp", 0)

            print("\n=== Optimum Pipeline Summary ===")
            print(f"Network Name: {optimum_result.get('network_name', 'N/A')}")
            print(f"Simulation Mode: {optimum_result.get('mode', 'N/A').capitalize()}")
            print(f"Inlet Flow Rate: {summary_data.get('inlet_flow', 0):.3f} m³/s")
            print(f"Outlet Flow Rate: {summary_data.get('outlet_flow', 0):.3f} m³/s")
            print(f"Total Pressure Drop: {self._format_pressure(summary_data.get('total_pressure_drop'))}")
            print(f"Total Head Loss: {summary_data.get('total_head_loss', 0):.2f} m")
            print(f"Total Power Required: {self._format_power(summary_data.get('total_power_required'))}")
            if residual_dp:
                print(f"Residual ΔP available for control valve: {residual_dp:.3f} kPa")

            return [{
                "network_name": optimum_result.get("network_name"),
                "simulation_mode": optimum_result.get("mode"),
                "inlet_flow": self._get_value(summary_data.get("inlet_flow", 0)),
                "outlet_flow": self._get_value(summary_data.get("outlet_flow", 0)),
                "total_pressure_drop": self._get_value(summary_data.get("total_pressure_drop", 0)),
                "total_head_loss": self._get_value(summary_data.get("total_head_loss", 0)),
                "total_power_required": self._get_value(summary_data.get("total_power_required", 0)),
                "residual_dp": residual_dp,
            }]

        # Top N results in tabular form
        top_results = self.get_top_n_results(top_n)
        if not top_results:
            print(f"No top {top_n} results found.")
            return []

        table = []
        summaries = []
        for i, result in enumerate(top_results):
            summary_data = result.get("summary", {})
            residual_dp = result.get("residual_dp", 0)
            summaries.append({
                "network_name": result.get("network_name"),
                "simulation_mode": result.get("mode"),
                "inlet_flow": self._get_value(summary_data.get("inlet_flow", 0)),
                "outlet_flow": self._get_value(summary_data.get("outlet_flow", 0)),
                "total_pressure_drop": self._get_value(summary_data.get("total_pressure_drop", 0)),
                "total_head_loss": self._get_value(summary_data.get("total_head_loss", 0)),
                "total_power_required": self._get_value(summary_data.get("total_power_required", 0)),
                "residual_dp": residual_dp,
            })
            table.append([
                i + 1,
                result.get("network_name", "N/A"),
                result.get("mode", "N/A").capitalize(),
                f"{summary_data.get('inlet_flow', 0):.3f}",
                f"{summary_data.get('outlet_flow', 0):.3f}",
                self._format_pressure(summary_data.get("total_pressure_drop")),
                f"{summary_data.get('total_head_loss', 0):.2f}",
                self._format_power(summary_data.get("total_power_required")),
                f"{residual_dp:.3f}"
            ])

        headers = ["#", "Network", "Mode", "Inlet Flow (m³/s)", "Outlet Flow (m³/s)",
                   "Pressure Drop", "Head Loss (m)", "Power", "Residual ΔP (kPa)"]
        print(f"\n=== Top {top_n} Pipeline Simulation Results ===")
        print(tabulate(table, headers=headers, tablefmt="grid"))

        return summaries

    # -------------------- Component details --------------------
    def detailed_summary(self, top_n: Optional[int] = 1) -> None:
        top_results = self.get_top_n_results(top_n)
        if not top_results:
            print(f"No results available for detailed summary of top {top_n}.")
            return

        for idx, result in enumerate(top_results):
            summary_data = result.get("summary", {})
            residual_dp = result.get("residual_dp", 0)
            print(f"\n=== Detailed Components for Result {idx+1} ({result.get('network_name', 'N/A')}) ===")
            print(f"Simulation Mode: {result.get('mode', 'N/A').capitalize()}")
            print(f"Inlet Flow: {summary_data.get('inlet_flow', 0):.3f} m³/s, "
                  f"Outlet Flow: {summary_data.get('outlet_flow', 0):.3f} m³/s, "
                  f"Total Pressure Drop: {self._format_pressure(summary_data.get('total_pressure_drop'))}, "
                  f"Residual ΔP: {residual_dp:.3f} kPa, "
                  f"Power: {self._format_power(summary_data.get('total_power_required'))}")

            components_data = result.get("components", [])
            if components_data:
                comp_table = []
                for comp in components_data:
                    comp_table.append([
                        comp.get("name") or comp.get("type", "Component"),
                        comp.get("type"),
                        self._format_pressure(comp.get("pressure_drop")),
                        comp.get("velocity"),
                        comp.get("reynolds_number"),
                        comp.get("friction_factor"),
                        comp.get("head_loss"),
                        self._format_power(comp.get("power")),
                    ])
                headers = ["Name", "Type", "Pressure Drop", "Velocity", "Re", "Friction Factor", "Head Loss", "Power"]
                print(tabulate(comp_table, headers=headers, tablefmt="grid"))

    # -------------------- Raw results & utility --------------------
    def to_dict(self) -> Dict[str, Any]:
        return self.results

    def add_info(self, key: str, value: Any) -> None:
        self.results.setdefault("extra_info", {})[key] = value

    # -------------------- Selection helpers --------------------
    def get_optimum_result(self, target_dp: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        top_results = self.get_top_n_results(1, target_dp)
        return top_results[0] if top_results else None

    def get_top_n_results(self, n: int, target_dp: Optional[Any] = None) -> List[Dict[str, Any]]:
        target = target_dp or self._target_dp
        if not self._all_simulation_results or not target:
            return []
        try:
            target_pa = target.to("Pa").value
        except (AttributeError, NotImplementedError):
            return []

        valid_results = [r for r in self._all_simulation_results if 'total_pressure_drop' in r.get('summary', {})]
        sorted_results = sorted(
            valid_results,
            key=lambda x: abs(x['summary']['total_pressure_drop'].to("Pa").value - target_pa)
        )
        return sorted_results[:n]
