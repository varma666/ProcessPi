# Optimum Pipe Diameter for Chlorine Gas

**Problem**  
Estimate the optimum pipe diameter for a flow of dry chlorine gas of **10 000 kg/h**  
at **6 atm(a)** and **20 °C** through a carbon steel pipe.

---

## Code

```python
from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine

# Define fluid and mass flow
fluid = Chlorine(temperature=Temperature(20, "C"), pressure=Pressure(6, "atm"))
mass_flow = MassFlowRate(10000, "kg/h")

print("Density:", fluid.density())

# Create engine without explicit network
model = PipelineEngine()
model.fit(fluid=fluid, mass_flow=mass_flow)
results = model.run()

results.summary()
results.detailed_summary()
```

## Output
```py
# Summary
Density: 17.685884 kg/m3
✅ Found optimal diameter based on recommended velocity.
   Selected Diameter: 8.0 in 
   Calculated Pressure Drop: 15.43 Pa
⚠️ Warning: Final velocity 4.87 m/s outside recommended range (5.00-10.00 m/s) for Chlorine.

=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 8 in 
Inlet Flow: 0.157 m3/s 
Outlet Flow: 0.157 m3/s
Total Pressure Drop: 0.02 kPa
Total Head Loss: 0.09 m
Total Power Required: 0.00 kW
Velocity: 4.867 m/s
Reynolds Number: 987160 (dimensionless)
Friction Factor: 0.0149 (dimensionless)


# Detailed Summary
=== Detailed Components for Result 1 (Main Pipe) ===
+-----------+--------+-----------------+------------+------------+-------------------+------------+
| Name      | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+===========+========+=================+============+============+===================+============+
| Main Pipe | pipe   |           15.43 |       4.87 |     987160 |            0.0149 | 8 in       |
+-----------+--------+-----------------+------------+------------+-------------------+------------+

```