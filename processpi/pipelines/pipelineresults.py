# processpi/pipelines/pipelineresults.py

from typing import Dict, Any
from ..units import Diameter, Length, Pressure

class PipelineResults:
    def __init__(self, results: dict):
        self.results = results

    def summary(self):
        """Print a clean, human-readable summary of the last run."""
        results = self.results
        if not results:
            print("No results available. Run the engine first.")
            return

        print("\n=== Pipeline Summary ===")

        # -------------------- Network summary --------------------
        summary = results.get("summary", {})
        if summary:
            inlet_flow = summary.get("inlet_flow_m3_s")
            total_dp = summary.get("total_pressure_drop_Pa")
            if inlet_flow:
                fval = inlet_flow.value if hasattr(inlet_flow, "value") else inlet_flow
                print(f"Inlet Flow: {fval:.3f} m³/s")
            if total_dp:
                fval = total_dp.value if hasattr(total_dp, "value") else total_dp
                print(f"Total Pressure Drop: {fval:.2f} Pa")

        # -------------------- Single Pipe Mode --------------------
        if results.get("mode") == "single":
            pipe_data = results.get("pipe", {})
            d = pipe_data.get("internal_diameter")
            l = pipe_data.get("length")
            v = results.get("velocity_m_s")
            Re = results.get("reynolds_number")
            f = results.get("friction_factor")
            dp = results.get("pressure_drop_Pa")

            print("\n--- Single Pipe ---")
            if d:
                print(f"Pipe Internal Diameter: {d.value:.2f} mm")
            if l:
                print(f"Pipe Length: {l.value:.2f} m")
            if v:
                print(f"Velocity: {v.value:.3f} m/s")
            if Re is not None:
                re_val = Re.value if hasattr(Re, "value") else Re
                print(f"Reynolds Number: {re_val:.0f}")
            if f is not None:
                fval = f.value if hasattr(f, "value") else f
                print(f"Friction Factor: {fval:.4f}")
            if dp:
                print(f"Pressure Drop: {dp.value:.2f} Pa")

        # -------------------- Network / Multiple Pipes --------------------
        pipes = results.get("pipes", [])
        if pipes:
            print("\n--- Pipe & Fitting Details ---")
            for p in pipes:
                if p["type"] == "pipe":
                    d = p.get("diameter_m")
                    v = p.get("velocity_m_s")
                    Re = p.get("reynolds_number")
                    f = p.get("friction_factor")
                    dp = p.get("pressure_drop_Pa")
                    print(f"\nPipe: {p.get('name','pipe')}")
                    if d:
                        d_val = d.value if hasattr(d, "value") else d
                        print(f"  Diameter: {d_val:.2f} mm")
                    if v:
                        v_val = v.value if hasattr(v, "value") else v
                        print(f"  Velocity: {v_val:.3f} m/s")
                    if Re is not None:
                        re_val = Re.value if hasattr(Re, "value") else Re
                        print(f"  Reynolds #: {re_val:.0f}")
                    if f is not None:
                        f_val = f.value if hasattr(f, "value") else f
                        print(f"  Friction Factor: {f_val:.4f}")
                    if dp:
                        dp_val = dp.value if hasattr(dp, "value") else dp
                        print(f"  Pressure Drop: {dp_val:.2f} Pa")
                elif p["type"] == "fitting":
                    dp = p.get("pressure_drop_Pa")
                    print(f"\nFitting: {p.get('name','fitting')}")
                    print(f"  K-factor: {p.get('K')}")
                    if dp:
                        dp_val = dp.value if hasattr(dp, "value") else dp
                        print(f"  Pressure Drop: {dp_val:.2f} Pa")

        # -------------------- Schematic --------------------
        if "schematic" in results:
            print("\n=== Schematic ===")
            print(results["schematic"])