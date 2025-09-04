from typing import Dict, Any, List, Optional
from tabulate import tabulate

from processpi.pipelines.standards import get_nearest_diameter
from ..units import Diameter, Velocity, Pressure, Power, Length, VolumetricFlowRate, Dimensionless


class PipelineResults:
    """
    Stores pipeline simulation results with full unit safety.
    Supports formatted summaries, detailed component tables, and raw exports.
    """

    def __init__(self, results: Dict[str, Any]):
        self.results: Dict[str, Any] = results
        self.network_name: str = results.get("network_name", "N/A")
        self.mode: str = results.get("mode", "single_pipe")
        self.residual_dp = results.get("residual_dp", 0)
        self._all_simulation_results: List[Dict[str, Any]] = []

        # Helper to coerce to plain float
        def _to_number(val: Any) -> float:
            if hasattr(val, "magnitude"):
                return float(val.magnitude)
            if hasattr(val, "value"):
                return float(val.value)
            if isinstance(val, (int, float)):
                return float(val)
            return 0.0

        # Normalize internal results for easy use
        if "all_simulation_results" in results:
            self._all_simulation_results = results["all_simulation_results"]
        elif "summary" in results and "components" in results:
            self._all_simulation_results = [{
                "network_name": self.network_name,
                "mode": self.mode,
                "summary": results["summary"],
                "components": results["components"],
                "residual_dp": self.residual_dp
            }]

        first_summary = (
            self._all_simulation_results[0].get("summary", {})
            if self._all_simulation_results else {}
        )

        # Units with safe numeric conversion
        self.inlet_flow = VolumetricFlowRate(_to_number(first_summary.get("flow_m3s", 0.0)), "m3/s")
        self.outlet_flow = VolumetricFlowRate(_to_number(first_summary.get("flow_m3s", 0.0)), "m3/s")
        self.total_pressure_drop = Pressure(_to_number(first_summary.get("total_pressure_drop_Pa", 0.0)), "Pa")
        self.total_head_loss = Length(_to_number(first_summary.get("total_head_m", 0.0)), "m")
        self.total_power_required = Power(_to_number(first_summary.get("pump_shaft_power_kW", 0.0)), "kW")
        self.velocity = Velocity(_to_number(first_summary.get("velocity", 0.0)), "m/s")
        self.reynolds = Dimensionless(_to_number(first_summary.get("reynolds", 0.0)))
        self.friction_factor = Dimensionless(_to_number(first_summary.get("friction_factor", 0.0)))

        # First component diameter
        first_component = (
            self._all_simulation_results[0].get("components", [{}])[0]
            if self._all_simulation_results else {}
        )
        diam_value = first_component.get("diameter", 0.0)
        self._pipe_diameter: Optional[Diameter] = (
            diam_value if isinstance(diam_value, Diameter)
            else Diameter(_to_number(diam_value)) if diam_value else None
        )

    # -------------------- Properties --------------------
    @property
    def pipe_diameter(self) -> Optional[Diameter]:
        return self._pipe_diameter

    # -------------------- Summaries --------------------
    def summary(self) -> List[Dict[str, Any]]:
        """Print and return a clean summary of results with units."""
        if not self._all_simulation_results:
            print("No simulation results available.")
            return []

        summaries = []
        for idx, result in enumerate(self._all_simulation_results):
            diameter = self.pipe_diameter

            print(f"\n=== Pipeline Result {idx+1} ({result.get('network_name', 'N/A')}) ===")
            print(f"Mode: {self.mode.capitalize()}")
            if diameter:
                print(f"Calculated Pipe Diameter: {get_nearest_diameter(diameter)} ")
            else:
                print(f"Calculated Pipe Diameter: N/A")
            print(f"Inlet Flow: {self.inlet_flow.to('m3/s'):.3f} ")
            print(f"Outlet Flow: {self.outlet_flow.to('m3/s'):.3f} ")
            print(f"Total Pressure Drop: {self.total_pressure_drop.to('kPa'):.2f}")
            print(f"Total Head Loss: {self.total_head_loss.to('m'):.2f}")
            print(f"Total Power Required: {self.total_power_required.to('kW'):.2f}")
            print(f"Velocity: {self.velocity.to('m/s'):.3f}")
            print(f"Reynolds Number: {self.reynolds:.0f}")
            print(f"Friction Factor: {self.friction_factor:.4f}")
            if self.residual_dp:
                print(f"Residual ΔP: {self.residual_dp:.3f}")

            summaries.append({
                "network_name": result.get("network_name"),
                "simulation_mode": self.mode,
                "pipe_diameter_in": diameter.to('in').value if diameter else None,
                "pipe_diameter_m": diameter.to('m').value if diameter else None,
                "inlet_flow_m3s": self.inlet_flow.to('m3/s').value,
                "outlet_flow_m3s": self.outlet_flow.to('m3/s').value,
                "total_pressure_drop_kPa": self.total_pressure_drop.to('kPa').value,
                "total_head_loss_m": self.total_head_loss.to('m').value,
                "total_power_required_kW": self.total_power_required.to('kW').value,
                "velocity_mps": self.velocity.to('m/s').value,
                "reynolds": self.reynolds.value,
                "friction_factor": self.friction_factor.value,
                "residual_dp_kPa": self.residual_dp,
            })

        return summaries


    def detailed_summary(self) -> None:
        """Print a component-level breakdown in table form.
        Supports both old-style (nested dict) and new-style (flat keys) results.
        Removes duplicate rows and fills missing types.
        """
        from tabulate import tabulate
        from processpi.units import Pressure, Velocity, Diameter

        if not self._all_simulation_results:
            print("No simulation results available.")
            return

        def _get_value_and_unit(val, default_val=0.0):
            """Safely extract value and unit from a variable."""
            unit = ""
            value = default_val
            if val is None:
                return default_val, unit
            if hasattr(val, "value"):
                value = float(val.value)
                if hasattr(val, "unit"):
                    unit = str(val.unit)
            elif hasattr(val, "magnitude"):
                value = float(val.magnitude)
                if hasattr(val, "units"):
                    unit = str(val.units)
            elif isinstance(val, (int, float, str)):
                try:
                    value = float(val)
                except ValueError:
                    value = default_val
            
            return value, unit

        for idx, result in enumerate(self._all_simulation_results):
            components = result.get("components", [])
            if not components:
                continue

            print(f"\n=== Detailed Components for Result {idx+1} ({result.get('network_name', 'N/A')}) ===")
            rows = []
            seen = set()  # to prevent duplicate rows

            for comp in components:

                def get_val(keys, default=None):
                    """Safe getter for nested or flat dict keys."""
                    for key in keys:
                        if "." in key:
                            parent, child = key.split(".", 1)
                            if isinstance(comp.get(parent), dict) and child in comp[parent]:
                                return comp[parent][child]
                        elif key in comp:
                            return comp[key]
                    return default

                # Extract variables directly
                pressure_var = get_val(["pressure_drop", "pressure_drop_Pa", "dp_Pa"])
                velocity_var = get_val(["velocity", "velocity_mps", "vel_mps"])
                reynolds_var = get_val(["reynolds"])
                friction_var = get_val(["friction_factor"])
                diameter_var = get_val(["diameter"])
                
                # Extract names and types
                name = comp.get("name") or comp.get("type", "Component")
                ctype = comp.get("type") or "Pipe"

                # Deduplicate rows based on component name and a key value
                key = (name, _get_value_and_unit(velocity_var)[0])
                if key in seen:
                    continue
                seen.add(key)
                
                # Get values and units
                pressure_val, pressure_unit = _get_value_and_unit(pressure_var)
                velocity_val, velocity_unit = _get_value_and_unit(velocity_var)
                reynolds_val, reynolds_unit = _get_value_and_unit(reynolds_var)
                friction_val, friction_unit = _get_value_and_unit(friction_var)
                
                # Handle diameter conversion and display
                diameter_display = "N/A"
                if isinstance(diameter_var, Diameter):
                    diameter_display = f"{get_nearest_diameter(diameter_var)}"
                elif diameter_var is not None:
                    diameter_val, diameter_unit = _get_value_and_unit(diameter_var)
                    diameter_display = f"{diameter_val:.2f} {diameter_unit}"

                # Append the raw values and their units to the row
                rows.append([
                    name,
                    ctype,
                    f"{pressure_val:.2f} {pressure_unit}",
                    f"{velocity_val:.2f} {velocity_unit}",
                    f"{reynolds_val:.2f} {reynolds_unit}",
                    f"{friction_val:.4f} {friction_unit}",
                    diameter_var if isinstance(diameter_var, str) else diameter_display
                ])

            headers = ["Name", "Type", "Pressure Drop", "Velocity", "Reynolds", "Friction Factor", "Diameter"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))

