# Water Transfer (Steel vs. Concrete Pipe)

**Problem**  
Transfer **100 000 kg/h** of water at **40 °C** from a canal to a reservoir.  

- Static head available: 6 m (0.58 atm)  
- Compare pipeline performance for **carbon steel** vs **concrete** pipe  
- Pipe length: 3200 m  

---

## Code

```python
from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe

# Define fluid and flow
fluid = Water(temperature=Temperature(40, "C"))
flow_rate = MassFlowRate(100000, "kg/h")
allowable_dp = Pressure(0.58, "atm")

# Define pipes
pipe_cs = Pipe(name="Steel Pipe", length=Length(3200, "m"), material="CS")
pipe_concrete = Pipe(name="Concrete Pipe", length=Length(3200, "m"), material="Concrete")

# Carbon steel model
model_cs = PipelineEngine()
model_cs.fit(fluid=fluid, pipe=pipe_cs, mass_flow=flow_rate, available_dp=allowable_dp)

# Concrete model
model_concrete = PipelineEngine()
model_concrete.fit(fluid=fluid, pipe=pipe_concrete, mass_flow=flow_rate, available_dp=allowable_dp)

# Run simulations
results_cs = model_cs.run()
results_concrete = model_concrete.run()

# Summaries
model_cs.summary()
results_cs.detailed_summary()

model_concrete.summary()
results_concrete.detailed_summary()
```

## Output

```py

✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 10.0 in (0.254 m)
   Calculated Pressure Drop: 31967.63 Pa (allowed: 58768.50 Pa)
⚠️ Warning: Final velocity 0.55 m/s outside recommended range (1.00-2.50 m/s) for Water.
✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 10.0 in (0.254 m)
   Calculated Pressure Drop: 41071.98 Pa (allowed: 58768.50 Pa)
⚠️ Warning: Final velocity 0.55 m/s outside recommended range (1.00-2.50 m/s) for Water.

# Summary
=== Pipeline Result 1 (Steel Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 10 in
Inlet Flow: 0.028 m3/s
Outlet Flow: 0.028 m3/s
Total Pressure Drop: 31.97 kPa
Total Head Loss: 3.30 m
Total Power Required: 1.28 kW
Velocity: 0.552 m/s
Reynolds Number: 207071 (dimensionless)
Friction Factor: 0.0169 (dimensionless)

# Detailed Summary
=== Detailed Components for Result 1 (Steel Pipe) ===
+------------+--------+-----------------+------------+------------+-------------------+------------+
| Name       | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+============+========+=================+============+============+===================+============+
| Steel Pipe | pipe   |         31967.6 |       0.55 |     207071 |            0.0169 | 10 in      |
+------------+--------+-----------------+------------+------------+-------------------+------------+

# Summary
=== Pipeline Result 1 (Concrete Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 10 in
Inlet Flow: 0.028 m3/s
Outlet Flow: 0.028 m3/s
Total Pressure Drop: 41.07 kPa
Total Head Loss: 4.24 m
Total Power Required: 1.65 kW
Velocity: 0.552 m/s
Reynolds Number: 207071 (dimensionless)
Friction Factor: 0.0217 (dimensionless)

# Detailed Summary
=== Detailed Components for Result 1 (Concrete Pipe) ===
+---------------+--------+-----------------+------------+------------+-------------------+------------+
| Name          | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+===============+========+=================+============+============+===================+============+
| Concrete Pipe | pipe   |           41072 |       0.55 |     207071 |            0.0217 | 10 in      |
+---------------+--------+-----------------+------------+------------+-------------------+------------+

```