from typing import Dict, Any, List, Optional
from tabulate import tabulate

class PipelineResults:
    """
    Manages pipeline simulation results using ProcessPI units
    and provides detailed summaries of network and components.
    """

    def __init__(self, results: Dict[str, Any]):
        self.results: Dict[str, Any] = results
        self.network_name: str = results.get("network_name", "N/A")
        self.mode: str = results.get("mode", "single_pipe")
        self.residual_dp = results.get("residual_dp", 0)
        self._all_simulation_results: List[Dict[str, Any]] = []

        # Flatten input results into internal list
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

        # Preprocess components to convert units to floats
        for result in self._all_simulation_results:
            if "components" in result:
                result["components"] = [self._convert_component_values(c) for c in result["components"]]

        # Reference first result for quick access
        first_result = self._all_simulation_results[0] if self._all_simulation_results else {}
        summary_data = first_result.get("summary", {})

        # Store top-level attributes with safe defaults
        self.inlet_flow = summary_data.get("inlet_flow") or 0.0
        self.outlet_flow = summary_data.get("outlet_flow") or 0.0
        self.total_pressure_drop = summary_data.get("total_pressure_drop") or 0.0
        self.total_head_loss = summary_data.get("total_head_loss") or 0.0
        self.total_power_required = summary_data.get("total_power_required") or 0.0
        self.velocity = summary_data.get("velocity") or 0.0
        self.reynolds = summary_data.get("reynolds") or 0.0
        self.friction_factor = summary_data.get("friction_factor") or 0.0
        self.components: List[Dict[str, Any]] = first_result.get("components", [])

    # -------------------- Internal helpers --------------------
    @staticmethod
    def _to_float(val: Any) -> Optional[float]:
        """Convert a ProcessPI unit object or numeric value to float."""
        if val is None:
            return None
        try:
            return float(val)
        except Exception:
            try:
                # If val has a `.value` attribute (common for units)
                return float(val.value)
            except Exception:
                return None

    def _convert_component_values(self, comp: Dict[str, Any]) -> Dict[str, Any]:
        """Convert all relevant ProcessPI unit objects to float for display."""
        keys = ["pressure_drop", "total_dp", "major_dp", "minor_dp", "elevation_dp",
                "velocity", "reynolds", "friction_factor", "diameter"]
        for k in keys:
            if k in comp:
                comp[k] = self._to_float(comp[k])
        return comp

    # -------------------- Formatting helpers --------------------
    @staticmethod
    def _format_pressure(val: Optional[float]) -> str:
        return f"{val:.2f}" if val is not None else "N/A"

    @staticmethod
    def _format_power(val: Optional[float]) -> str:
        return f"{val:.2f}" if val is not None else "N/A"

    @staticmethod
    def _format_velocity(val: Optional[float]) -> str:
        return f"{val:.3f}" if val is not None else "N/A"

    @staticmethod
    def _format_reynolds(val: Optional[float]) -> str:
        return f"{val:.2f}" if val is not None else "N/A"

    @staticmethod
    def _format_friction(val: Optional[float]) -> str:
        return f"{val:.4f}" if val is not None else "N/A"

    @staticmethod
    def _format_diameter(diam) -> str:
        """Convert Diameter object to string if necessary."""
        if diam is None:
            return "N/A"
        try:
            return f"{float(diam):.3f} m"
        except Exception:
            return str(diam)

    # -------------------- Pipe diameter property --------------------
    @property
    def pipe_diameter(self) -> Optional[Any]:
        """Return the calculated optimum pipe diameter, if available."""
        if self.components and "diameter" in self.components[0]:
            return self.components[0]["diameter"]
        return self.results.get("diameter", None)

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

            inlet_flow = summary_data.get("inlet_flow") or 0.0
            outlet_flow = summary_data.get("outlet_flow") or 0.0
            total_head_loss = summary_data.get("total_head_loss") or 0.0
            total_power = summary_data.get("total_power_required") or 0.0
            velocity = summary_data.get("velocity") or 0.0
            reynolds = summary_data.get("reynolds") or 0.0
            friction_factor = summary_data.get("friction_factor") or 0.0
            total_pressure = summary_data.get("total_pressure_drop") or 0.0

            print(f"\n=== Pipeline Result {idx+1} ({result.get('network_name', 'N/A')}) ===")
            print(f"Mode: {result.get('mode', 'N/A').capitalize()}")
            print(f"Calculated Pipe Diameter: {self._format_diameter(diameter)}")
            print(f"Inlet Flow: {inlet_flow:.3f} m³/s")
            print(f"Outlet Flow: {outlet_flow:.3f} m³/s")
            print(f"Total Pressure Drop: {self._format_pressure(total_pressure)} Pa")
            print(f"Total Head Loss: {total_head_loss:.2f} m")
            print(f"Total Power Required: {self._format_power(total_power)} kW")
            print(f"Velocity: {self._format_velocity(velocity)} m/s")
            print(f"Reynolds Number: {self._format_reynolds(reynolds)}")
            print(f"Friction Factor: {self._format_friction(friction_factor)}")
            if residual_dp:
                print(f"Residual ΔP: {residual_dp:.3f} kPa")

            summaries.append({
                "network_name": result.get("network_name"),
                "simulation_mode": result.get("mode"),
                "pipe_diameter": diameter,
                "inlet_flow": inlet_flow,
                "outlet_flow": outlet_flow,
                "total_pressure_drop": total_pressure,
                "total_head_loss": total_head_loss,
                "total_power_required": total_power,
                "velocity": velocity,
                "reynolds": reynolds,
                "friction_factor": friction_factor,
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
            print(f"Inlet Flow: {(summary_data.get('inlet_flow') or 0.0):.3f} m³/s, "
                  f"Outlet Flow: {(summary_data.get('outlet_flow') or 0.0):.3f} m³/s, "
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
                        self._format_pressure(comp.get("total_dp") or comp.get("pressure_drop")),
                        self._format_velocity(comp.get("velocity")),
                        self._format_reynolds(comp.get("reynolds")),
                        self._format_friction(comp.get("friction_factor")),
                        self._format_pressure(comp.get("major_dp")),
                        self._format_pressure(comp.get("minor_dp")),
                        self._format_pressure(comp.get("elevation_dp")),
                    ])
                headers = ["Name", "Type", "Pressure Drop", "Velocity", "Re", "Friction Factor",
                           "Major ΔP", "Minor ΔP", "Elevation ΔP"]
                print(tabulate(comp_table, headers=headers, tablefmt="grid"))

    # -------------------- Raw results --------------------
    def to_dict(self) -> Dict[str, Any]:
        return self.results
