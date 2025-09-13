# Organic Liquid Discharge Line


**Problem**

Organic liquid at 5000 kg/h, 50 °C, ρ = 930 kg/m³, μ = 0.91 cP.  
Line includes 50 m pipe, 6 elbows, 2 tees, 4 gate valves, 1 globe valve, 1 orifice meter.

## Code

```python
from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

# Define fluid properties
fluid = OrganicLiquid(density=Density(930, "kg/m3"), viscosity=Viscosity(0.91, "cP"))
mass_flow = MassFlowRate(5000, "kg/h")

# Define pipeline
pipe = Pipe(name="Organic Liquid Pipe", length=Length(50, "m"))
fittings = [
    Fitting("standard_elbow_90_deg", quantity=6),
    Fitting("standard_tee_through_flow", quantity=2),
    Fitting("gate_valve", quantity=4),
    Fitting("globe_valve", quantity=1),
    Fitting("sudden_contraction", quantity=1),
]

# Build and run model
model = PipelineEngine()
model.fit(fluid=fluid, mass_flow=mass_flow, pipe=pipe, fittings=fittings)
results = model.run()

# Display results
model.summary()
results.detailed_summary()
```

## Output

```py

✅ Found optimal diameter based on recommended velocity.
   Selected Diameter: 1.5 in 
   Calculated Pressure Drop: 27024.74 Pa
⚠️ Warning: Final velocity 1.14 m/s outside recommended range (1.80-2.00 m/s) for Organic Liquid.

# Summary
=== Pipeline Result 1 (Organic Liquid Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 1.5 in 
Inlet Flow: 0.001 m3/s 
Outlet Flow: 0.001 m3/s 
Total Pressure Drop: 27.02 kPa
Total Head Loss: 2.96 m
Total Power Required: 0.06 kW
Velocity: 1.139 m/s
Reynolds Number: 47546 (dimensionless)
Friction Factor: 0.0245 (dimensionless)

# Detailed Summary
=== Detailed Components for Result 1 (Organic Liquid Pipe) ===
+---------------------+--------+-----------------+------------+------------+-------------------+------------+
| Name                | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+=====================+========+=================+============+============+===================+============+
| Organic Liquid Pipe | pipe   |         27024.7 |       1.14 |    47545.9 |            0.0245 | 1.5 in     |
+---------------------+--------+-----------------+------------+------------+-------------------+------------+

```