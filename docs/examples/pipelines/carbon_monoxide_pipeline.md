# Carbon Monoxide Pipeline

**Problem**  
Design a CO pipeline with the following specifications:  

- Inlet pressure: 50 kPa(g)  
- Pipe length: 4 km  
- Flow rate: 1500 kg/h  
- Fittings: 2 gate valves, 3 × 45° elbows, 6 × 90° elbows  

---

## Code

```python
from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

# Define fluid
fluid = CarbonMonoxide(temperature=Temperature(50, "C"))

# Define flow
mass_flow = MassFlowRate(1500, "kg/h")

# Pipe and fittings
pipe = Pipe(name="Main Pipe", length=Length(4, "km"), material="CS")
valves = Fitting(fitting_type="gate_valve", quantity=2)
elbows_45 = Fitting(fitting_type="standard_elbow_45_deg", quantity=3)
elbows_90 = Fitting(fitting_type="standard_elbow_90_deg", quantity=6)

# Build and run model
model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbows_45, elbows_90, valves],
    available_dp=Pressure(50, "kPa")
)
results = model.run()

# Summaries
model.summary()
print("Pressure drop (atm):", results.total_pressure_drop.to("atm"))
results.detailed_summary()
```

## Output
```py
✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 8.0 in (0.2027 m internal)
   Calculated Pressure Drop: 28824.94 Pa (allowed: 50000.00 Pa)

# Summary
=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Nominal Pipe Size: 8 in
Internal Diameter: 202.74 mm
Inlet Flow: 0.394 m3/s 
Outlet Flow: 0.394 m3/s 
Total Pressure Drop: 28.82 kPa
Total Head Loss: 2782.64 m
Total Power Required: 16.24 kW
Velocity: 12.219 m/s
Reynolds Number: 137203 (dimensionless)
Friction Factor: 0.0182 (dimensionless)
Pressure drop (atm): 0.28448 atm

# Detailed Summary
=== Detailed Components for Result 1 (Main Pipe) ===
+-----------+--------+-----------------+------------+------------+-------------------+----------------+---------------------+
| Name      | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Nominal Size   | Internal Diameter   |
+===========+========+=================+============+============+===================+================+=====================+
| Main Pipe | pipe   |         28824.9 |      12.22 |     137203 |            0.0182 | 8 in           | 202.74 mm           |
+-----------+--------+-----------------+------------+------------+-------------------+----------------+---------------------+

```