from typing import Dict, Any, List, Optional
from tabulate import tabulate
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
                print(f"Calculated Pipe Diameter: {diameter.to('in'):.2f}  ({diameter.to('m'):.3f})")
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

        if not self._all_simulation_results:
            print("No simulation results available.")
            return

        def _to_number(val, default=0.0):
            """Safely convert unit-wrapped or raw values to float."""
            if val is None:
                return default
            if hasattr(val, "value"):  # Units with .value attribute
                return float(val.value)
            if hasattr(val, "magnitude"):  # Pint or similar units
                return float(val.magnitude)
            if isinstance(val, (int, float, str)):
                try:
                    return float(val)
                except ValueError:
                    return default
            return default

        for idx, result in enumerate(self._all_simulation_results):
            components = result.get("components", [])
            if not components:
                continue

            print(f"\n=== Detailed Components for Result {idx+1} ({result.get('network_name', 'N/A')}) ===")
            rows = []
            seen = set()  # to prevent duplicate rows

            for comp in components:

                def get_val(keys, default=0.0):
                    """Safe getter for nested or flat dict keys."""
                    for key in keys:
                        if "." in key:
                            parent, child = key.split(".", 1)
                            if isinstance(comp.get(parent), dict) and child in comp[parent]:
                                return comp[parent][child]
                        elif key in comp:
                            return comp[key]
                    return default

                # Extract values
                pressure_val = get_val(["pressure_drop.value", "pressure_drop", "pressure_drop_Pa", "dp_Pa"])
                velocity_val = get_val(["velocity.value", "velocity", "velocity_mps", "vel_mps"])
                reynolds_val = get_val(["reynolds.value", "reynolds"])
                friction_val = get_val(["friction_factor.value", "friction_factor"])
                diameter_val = get_val(["diameter"])

                # Convert diameter to object
                if isinstance(diameter_val, Diameter):
                    diameter_obj = diameter_val
                elif diameter_val:
                    diameter_obj = Diameter(_to_number(diameter_val,"m").value)
                else:
                    diameter_obj = None

                name = comp.get("name") or comp.get("type", "Component")
                ctype = comp.get("type") or "Pipe"

                # Deduplicate rows based on component name and diameter
                key = (name, round(_to_number(velocity_val), 4))
                if key in seen:
                    continue
                seen.add(key)

                rows.append([
                    name,
                    ctype,
                    Pressure(_to_number(pressure_val), "Pa").to("kPa").value,
                    Velocity(_to_number(velocity_val), "m/s").to("m/s").value,
                    _to_number(reynolds_val),
                    _to_number(friction_val),
                    diameter_obj.to("in") if diameter_obj else None,
                ])

            headers = ["Name", "Type", "ΔP (kPa)", "Velocity (m/s)", "Re", "Friction", "Diameter (in)"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))

