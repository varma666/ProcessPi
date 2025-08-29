from typing import Dict, Any, List, Optional
from tabulate import tabulate

class PipelineResults:
    """Manages pipeline simulation results using ProcessPI units and detailed component breakdowns."""

    def __init__(self, results: Dict[str, Any]):
        self.results: Dict[str, Any] = results
        self.network_name: str = results.get("network_name", "N/A")
        self.mode: str = results.get("mode", "single_pipe")
        self.residual_dp = results.get("residual_dp", 0)
        self._all_simulation_results: List[Dict[str, Any]] = []

        # Flatten input results to internal list
        if "all_simulation_results" in results:
            self._all_simulation_results = results["all_simulation_results"]
        elif "summary" in results and "components" in results:
            summary = results["summary"]
            comps = results["components"]
            self._all_simulation_results = [{
                "network_name": self.network_name,
                "mode": self.mode,
                "summary": {
                    "inlet_flow": summary.get("flow_m3s"),
                    "outlet_flow": summary.get("flow_m3s"),
                    "total_pressure_drop": summary.get("total_pressure_drop_Pa"),
                    "total_head_loss": summary.get("total_head_m"),
                    "total_power_required": summary.get("pump_shaft_power_kW"),
                    "velocity": comps[0].get("velocity") if comps else None,
                    "reynolds": comps[0].get("reynolds") if comps else None,
                    "friction_factor": comps[0].get("friction_factor") if comps else None,
                },
                "residual_dp": self.residual_dp,
                "components": comps,
            }]

        first_result = self._all_simulation_results[0] if self._all_simulation_results else {}
        summary_data = first_result.get("summary", {})

        # Store as ProcessPI variables for calculations
        self.inlet_flow = summary_data.get("inlet_flow")
        self.outlet_flow = summary_data.get("outlet_flow")
        self.total_pressure_drop = summary_data.get("total_pressure_drop")
        self.total_head_loss = summary_data.get("total_head_loss")
        self.total_power_required = summary_data.get("total_power_required")
        self.velocity = summary_data.get("velocity")
        self.reynolds = summary_data.get("reynolds")
        self.friction_factor = summary_data.get("friction_factor")
        self.components: List[Dict[str, Any]] = first_result.get("components", [])

    # -------------------- Console formatting --------------------
    @staticmethod
    def _format_pressure(val) -> str:
        return f"{val:.2f}" if val is not None else "N/A"

    @staticmethod
    def _format_power(val) -> str:
        return f"{val:.2f}" if val is not None else "N/A"

    @staticmethod
    def _format_velocity(val) -> str:
        return f"{val:.3f}" if val is not None else "N/A"

    @staticmethod
    def _format_reynolds(val) -> str:
        return f"{val:.2f}" if val is not None else "N/A"

    @staticmethod
    def _format_friction(val) -> str:
        return f"{val:.4f}" if val is not None else "N/A"

    # -------------------- Main summaries --------------------
    def summary(self) -> List[Dict[str, Any]]:
        if not self._all_simulation_results:
            print("No simulation results available.")
            return []

        summaries = []
        for idx, result in enumerate(self._all_simulation_results):
            summary_data = result.get("summary", {})
            residual_dp = result.get("residual_dp", 0)
            diameter = self.pipe_diameter

            print(f"\n=== Pipeline Result {idx+1} ({result.get('network_name', 'N/A')}) ===")
            print(f"Mode: {result.get('mode', 'N/A').capitalize()}")
            if diameter:
                print(f"Calculated Pipe Diameter: {diameter}")
            print(f"Inlet Flow: {summary_data.get('inlet_flow', 0):.3f} m³/s")
            print(f"Outlet Flow: {summary_data.get('outlet_flow', 0):.3f} m³/s")
            print(f"Total Pressure Drop: {self._format_pressure(summary_data.get('total_pressure_drop'))}")
            print(f"Total Head Loss: {summary_data.get('total_head_loss', 0):.2f} m")
            print(f"Total Power Required: {self._format_power(summary_data.get('total_power_required'))}")
            print(f"Velocity: {self._format_velocity(summary_data.get('velocity'))}")
            print(f"Reynolds Number: {self._format_reynolds(summary_data.get('reynolds'))}")
            print(f"Friction Factor: {self._format_friction(summary_data.get('friction_factor'))}")
            if residual_dp:
                print(f"Residual ΔP: {residual_dp:.3f} kPa")

            summaries.append({
                "network_name": result.get("network_name"),
                "simulation_mode": result.get("mode"),
                "pipe_diameter": diameter,
                "inlet_flow": summary_data.get("inlet_flow"),
                "outlet_flow": summary_data.get("outlet_flow"),
                "total_pressure_drop": summary_data.get("total_pressure_drop"),
                "total_head_loss": summary_data.get("total_head_loss"),
                "total_power_required": summary_data.get("total_power_required"),
                "velocity": summary_data.get("velocity"),
                "reynolds": summary_data.get("reynolds"),
                "friction_factor": summary_data.get("friction_factor"),
                "residual_dp": residual_dp,
            })
        return summaries

    # -------------------- Detailed component summaries --------------------
    def detailed_summary(self) -> None:
        if not self._all_simulation_results:
            print("No simulation results available.")
            return

        for idx, result in enumerate(self._all_simulation_results):
            summary_data = result.get("summary", {})
            residual_dp = result.get("residual_dp", 0)
            print(f"\n=== Detailed Components for Result {idx+1} ({result.get('network_name', 'N/A')}) ===")
            print(f"Mode: {result.get('mode', 'N/A').capitalize()}")
            print(f"Inlet Flow: {summary_data.get('inlet_flow', 0):.3f} m³/s, "
                  f"Outlet Flow: {summary_data.get('outlet_flow', 0):.3f} m³/s, "
                  f"Total Pressure Drop: {self._format_pressure(summary_data.get('total_pressure_drop'))}, "
                  f"Residual ΔP: {residual_dp:.3f} kPa, "
                  f"Power: {self._format_power(summary_data.get('total_power_required'))}, "
                  f"Velocity: {self._format_velocity(summary_data.get('velocity'))}, "
                  f"Re: {self._format_reynolds(summary_data.get('reynolds'))}, "
                  f"Friction Factor: {self._format_friction(summary_data.get('friction_factor'))}")

            components_data = result.get("components", [])
            if components_data:
                comp_table = []
                for comp in components_data:
                    comp_table.append([
                        comp.get("name") or comp.get("type", "Component"),
                        comp.get("type"),
                        comp.get("total_dp") or comp.get("pressure_drop"),
                        comp.get("velocity"),
                        comp.get("reynolds"),
                        comp.get("friction_factor"),
                        comp.get("major_dp"),
                        comp.get("minor_dp"),
                        comp.get("elevation_dp"),
                    ])
                headers = ["Name", "Type", "Pressure Drop", "Velocity", "Re", "Friction Factor",
                           "Major ΔP", "Minor ΔP", "Elevation ΔP"]
                print(tabulate(comp_table, headers=headers, tablefmt="grid"))

    # -------------------- Raw results --------------------
    def to_dict(self) -> Dict[str, Any]:
        return self.results
    
    @property
    def pipe_diameter(self) -> Optional[Any]:
        """Return the calculated optimum pipe diameter, if available."""
        # Usually stored in results under 'diameter' or in first component
        if self.components and "diameter" in self.components[0]:
            return self.components[0]["diameter"]
        return self.results.get("diameter", None)
