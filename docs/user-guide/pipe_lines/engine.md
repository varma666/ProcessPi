# ProcessPI Pipeline Engine – API Reference & Feature Sheet

---

## 🔹 API – `PipelineEngine` Class

The **`PipelineEngine`** is the main interface for pipeline network analysis in ProcessPI.  
It performs **component-wise and network-wide calculations**, including **pressure drops, velocities, Reynolds numbers, friction factors**, and **optimum pipe sizing**.

### Methods

| Method | Description |
|--------|-------------|
| `fit(fluid, mass_flow=None, volumetric_flow=None, pipeline_network=None)` | Optimizes the pipeline design for a given flow rate. Calculates recommended pipe diameters and velocities. |
| `run()` | Performs full network analysis using the optimized diameters. Returns detailed results including component-wise and network summaries. |
| `calculate_pressure_drop(component, fluid, flow_rate)` | Computes pressure drop for a single pipe or fitting. |
| `calculate_velocity(component, flow_rate)` | Calculates average fluid velocity in a pipe. |
| `calculate_reynolds(component, fluid, flow_rate)` | Determines the Reynolds number for the component. |
| `calculate_friction_factor(component, reynolds)` | Computes Darcy friction factor based on flow regime. |
| `network_summary(pipeline_network, fluid, flow_rate)` | Returns network-level summary, including total pressure drop, total head loss, pump power, velocity, and Reynolds number. |
| `component_summary(pipeline_network, fluid, flow_rate)` | Returns component-level results, including DP, velocity, Reynolds, and friction factor. |

---

## ⚙️ Engine Helper Functions

The pipeline engine uses internal helper functions for standard calculations:

- `get_k_factor()` → Returns the **resistance factor** for fittings and bends.  
- `get_roughness()` → Provides the **surface roughness** for pipe materials.  
- `list_available_pipe_diameters()` → Returns standard pipe diameters.  
- `get_recommended_velocity()` → Provides recommended velocity for the application.  

These helpers abstract **lookup tables and engineering standards**, simplifying pipeline analysis for users.

---

## ✅ Key Features

### 1. Single Pipeline Analysis
- Pressure drop and flow rate calculations using:
  - **Darcy–Weisbach** for engineering-grade precision.
  - **Hazen–Williams** for water and low-viscosity fluids.
- Includes effects of:
  - Elevation (static head)
  - Pipe roughness
  - Fittings and valves (via K-factors)

### 2. Network Analysis
- Handles **branched and looped networks**:
  - Hardy–Cross iteration method
  - Direct matrix solver for node balancing
- Suitable for:
  - Small-to-medium plant utility networks
  - Firewater loops
  - Cooling water distribution

### 3. Component Loss Modeling
- Supports inline equipment and fittings:
  - Gate valves, globe valves, bends, tees
  - Orifice meters and filters
- Uses **industry-standard K-factor** data for accurate loss modeling.

### 4. Elevation and Static Head
- Node elevations automatically included in pressure and head balance.
- Useful for:
  - Hilly terrain installations
  - Overhead storage tanks
  - Sump-to-tank transfers

### 5. Multiple Solver Options

| Solver | Best For | Notes |
|--------|----------|-------|
| **Darcy–Weisbach** | Engineering-grade precision | Supports custom fluid properties |
| **Hazen–Williams** | Quick checks for water lines | Assumes low viscosity |
| **Hardy–Cross** | Small/medium networks with ≤10 pipes | Easy to debug |
| **Matrix Solver** | Networks with moderate branching | Faster and more robust |

### 6. Typical Use Cases
- Utility water network design  
- Chemical transfer line sizing  
- Cooling water loop balancing  
- Firewater ring main analysis  
- Static head impact studies

### 7. Current Limitations
- Steady-state only (no transient or surge analysis)  
- Single-phase fluids (no two-phase or slurry modeling)  
- Assumes constant density and viscosity  
- No integration with pump curves  
- Limited scalability for very large networks (>50 pipes)

### 8. Planned Roadmap

| Stage | Planned Feature |
|--------|----------------|
| **Short-term** | Newton–Raphson loop-and-node solver for larger networks |
| **Mid-term** | Pump curve integration and automatic pump-point calculation |
| **Mid-term** | Compressible (gas) network support |
| **Long-term** | Dynamic and transient simulation (surge, water hammer) |
| **Long-term** | Two-phase and slurry flow models |

---

## 💻 Example Usage

### Example 1 – Dry Chlorine Gas Pipeline

```python
from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine

# Define fluid and mass flow
fluid = Chlorine(temperature=Temperature(20, "C"), pressure=Pressure(6, "atm"))
mass_flow = MassFlowRate(10000, "kg/h")

print(fluid.density())

# Create engine without an explicit network
model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow
    # realistic pipe length can be added
)
results = model.run()  # auto diameter sizing
results.summary()
results.detailed_summary()
```